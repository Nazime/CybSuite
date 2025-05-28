import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

import dateutil.parser
from cybsuite.consts import (
    FOLDER_NAME_REPORTS,
    FOLDER_NAME_REVIEW,
    FOLDER_NAME_UNARCHIVED,
)
from cybsuite.core.logger import get_logger
from cybsuite.cyberdb import CyberDB, CyberDBScanManager, pm_reporters
from cybsuite.review.consts import FILENAME_INFO
from cybsuite.workspace.workspaces import get_current_workspace_path

from .base_reviewer import BaseReviewer, ReviewContext, pm_reviewers, pm_type_reviewers
from .extractions import ExtractionManager


class ReviewManager:
    """Manages the review process for files."""

    def __init__(
        self,
        *,
        cyberdb: CyberDB | None = None,
        force: bool = None,
        plugins_names: list[str] = None,
        plugins_category: Optional[str] = None,
        plugins_sub_category: Optional[str] = None,
        plugins_tags: Optional[List[str]] = None,
        plugins_authors: Optional[List[str]] = None,
        controls: Optional[List[str]] = None,
        open_report: bool = False,
    ):
        if cyberdb is None:
            cyberdb = CyberDB.from_default_config()
        self.logger = get_logger()
        self.force = force
        self.category = plugins_category
        self.sub_category = plugins_sub_category
        self.tags = plugins_tags
        self.authors = plugins_authors
        self.controls = controls
        self.open_report = open_report
        self.plugins_names = self._filter_plugins_names(plugins_names)

        self.cyberdb = cyberdb
        self.scan_manager = CyberDBScanManager(cyberdb=self.cyberdb)
        self.review_type = "windows"
        self.unarchived_path = (
            get_current_workspace_path()
            / FOLDER_NAME_REVIEW
            / FOLDER_NAME_UNARCHIVED
            / self.review_type
        )
        self.reports_path = (
            get_current_workspace_path() / FOLDER_NAME_REVIEW / FOLDER_NAME_REPORTS
        )
        self.extraction_manager = ExtractionManager()
        self.run_object = None

    def run(
        self,
        paths_to_review: List[str | Path],
    ):
        """Run the complete review process.

        Global algorithm
        for host in hosts:
            type_reviewer.prepare_for_host()
            for plugin in plugins:
                plugin.run(host)
            type_reviewer.cleanup_for_host()
            for plugin in plugins:
                plugin.post_run()

        """
        self.paths_to_review = paths_to_review
        self.logger.info("Starting review")

        # Initialize run object
        started_time = datetime.now(timezone.utc)
        self.run_object = self.cyberdb.create(
            "run", tool="cybs-review", status="running", start_time=started_time
        )

        # Extract files
        result_paths = self._extract_files()
        host_paths = list(
            e for e in self.unarchived_path.iterdir() if e in result_paths
        )

        self.type_reviewer = pm_type_reviewers["windows"]()

        # Get and process reviewers
        reviewers = self._get_reviewers()
        self._process_reviews(reviewers, host_paths)

        # Finalize run object
        ended_time = datetime.now(timezone.utc)
        self.run_object.end_time = ended_time
        self.run_object.status = "finished"
        self.run_object.save()
        self.scan_manager.print_stats()

        # Generate reports
        self._generate_reports()

    def review_extracts(self, *args, **kwargs):
        return self._run(*args, **kwargs)

    def review_files(self, files: List[str | Path]):
        # Normalize files to Path
        files = {k: Path(v) for k, v in files.items()}

        for plugin_name in self.plugins_names:
            plugin = pm_reviewers[plugin_name](self.cyberdb)
            plugin.run(files)

            plugin.post_run()

    # PRIVATE METHODS #
    # =============== #
    def _filter_plugins_names(self, plugins_names):
        if plugins_names is None:
            return [e.name for e in pm_reviewers]

        return plugins_names

    def _extract_files(self) -> List[Path]:
        """Extract files using the ExtractionManager."""
        return self.extraction_manager.extract_all(
            self.paths_to_review, force=self.force
        )

    def _get_reviewers(self):
        """Get and initialize the reviewers based on filters."""
        reviewers = pm_reviewers.iter(
            name=self.plugins_names,
            category=self.category,
            sub_category=self.sub_category,
            tags=self.tags,
            authors=self.authors,
        )
        reviewers = list(reviewers)
        return list(reviewer(self.cyberdb) for reviewer in reviewers)

    def _process_host(self, plugin, host_path: Path):
        """Process a single host with the given plugin."""
        plugin.enable_printing = True
        host_info_path = host_path / "info.json"

        with open(host_info_path, encoding="utf-8-sig") as f:
            host_info = json.load(f)

        hostname = host_info["name"]
        context = ReviewContext(
            hostname=hostname,
            datetime=dateutil.parser.parse(host_info["datetime"]),
            host_extracts_path=host_path,
        )

        plugin.context = context
        plugin.aditional_details = {"hostname": hostname}
        plugin.aditional_kwargs = {"latest_run": self.run_object}

        files = {}
        for key, value in plugin.files.items():
            files[key] = os.path.join(host_path, value)

        with self.scan_manager:
            plugin.run(files)

    def _process_reviews(self, reviewers, host_paths):
        """Process all reviews for the given hosts."""
        self.logger.info(
            f"Running {len(reviewers)} plugins on {len(host_paths)} Windows hosts"
        )
        last_host = None
        for plugin, host_path in self.scan_manager.iter_plugins(
            host_paths,
            plugins=reviewers,
            plugin_manager=pm_reviewers,
            iterator_description=lambda path: f"Processing host [cyan]{path.name}[/cyan]...",
        ):
            plugin.type_reviewer = self.type_reviewer

            if last_host != host_path:
                # Starting review of a new host
                self.logger.info(
                    f"Starting review of host [cyan]{host_path.name}[/cyan]..."
                )
                plugin.type_reviewer.prepare_for_host()

            self._process_host(plugin, host_path)
            last_host = host_path

        for plugin in reviewers:
            plugin.post_run()

    def _generate_reports(self):
        """Generate reports for the review process."""
        for reporter_class in pm_reporters:
            if reporter_class.name in ["html", "controls_json"]:
                configuration = {"latest_run": self.run_object}
            else:
                configuration = {}

            extension = reporter_class.extension or ""
            report_path = self.reports_path / f"{reporter_class.name}{extension}"
            self.logger.info(
                f"Generating '{reporter_class.name}' report: '{report_path}'"
            )

            reporter = reporter_class(cyberdb=self.cyberdb)
            reporter.configure(**configuration)
            try:
                reporter.run(report_path)
            except Exception as e:
                self.logger.error(f"Error generating {report_path} report: {e}")

            if reporter_class.name == "html" and self.open_report:
                self._open_file(report_path)

    def _open_file(self, path: str | Path):
        """Open a file in the default program for the current platform."""
        if sys.platform == "linux":
            subprocess.run(["xdg-open", path])
        # TODO: add windows support
