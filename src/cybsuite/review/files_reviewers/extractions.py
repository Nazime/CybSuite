import hashlib
import json
import os
import shutil
import zipfile
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional

from cybsuite.consts import (
    FILE_NAME_DATA,
    FOLDER_NAME_EXTRACTS,
    FOLDER_NAME_LOGS,
    FOLDER_NAME_REPORTS,
    FOLDER_NAME_REVIEW,
    FOLDER_NAME_UNARCHIVED,
)
from cybsuite.core.logger import get_logger
from cybsuite.review.consts import FILENAME_INFO
from cybsuite.workspace.workspaces import get_current_workspace_path

logger = get_logger()


@dataclass
class CachedData:
    """Data class for tracking cached data."""

    extracted_archives: set[str] = field(default_factory=set)


class ExtractionManager:
    """Manages the extraction of zip files and tracks extraction status."""

    def __init__(self, output_path: Optional[Path] = None):
        """Initialize the extraction manager.

        Args:
            output_path: Path where extracted files will be stored.
                         If None, uses the current workspace's review directory.
        """
        if output_path is None:
            self.output_path = get_current_workspace_path() / FOLDER_NAME_REVIEW
        else:
            self.output_path = output_path

        self._data_file_path = self.output_path / FILE_NAME_DATA
        self._data = CachedData()  # Use the dataclass
        self._load_data()

    def extract_one(self, path_to_extract: str | Path, force: bool = False) -> Path:
        """Extract a single zip file to the output path.

        Args:
            path_to_extract: Path to the zip file to extract
            force: If True, overwrite existing folders
        """
        path_to_extract = Path(path_to_extract)

        # Check file is correct zip file
        if not zipfile.is_zipfile(path_to_extract):
            raise ValueError(f"File '{path_to_extract}' is not a valid zip file")

        # Get the info.json from the zip file
        info = self._get_info_from_zip(path_to_extract)
        review_type = info["type"]
        name = info["name"]

        # Set up paths
        unarchived_type_path = self.output_path / FOLDER_NAME_UNARCHIVED / review_type
        extract_dest_path = unarchived_type_path / name
        reports_path = self.output_path / FOLDER_NAME_REPORTS
        result_path = unarchived_type_path / name
        # Check if already extracted
        info_hash = self._get_hash_from_info(info)
        if result_path.exists() and info_hash in self._data.extracted_archives:
            logger.info(
                f"Archive '{path_to_extract}' has already been extracted. Skipping extraction."
            )
            return result_path

        # Create necessary directories
        unarchived_type_path.mkdir(parents=True, exist_ok=True)
        reports_path.mkdir(parents=True, exist_ok=True)

        # Extract files
        logger.info(f"Extracting archive '{path_to_extract}' to '{extract_dest_path}'")
        self.extract_zip(path_to_extract, dest=unarchived_type_path)

        # Rename zip to hostname only
        root_dir = self.get_unique_root_dir_from_zip(path_to_extract)
        extracted_path = unarchived_type_path / Path(root_dir).name
        extracted_path.replace(result_path)

        # Save extraction data
        self._data.extracted_archives.add(info_hash)
        self._save_data()
        return result_path

    def extract_all(self, paths: list[str | Path], force: bool = False):
        """Extract multiple zip files.

        Args:
            paths: List of paths to zip files to extract
            force: If True, overwrite existing folders
        """
        # TODO: handle both files and folders
        result_paths = []
        for path in paths:
            result_paths.append(self.extract_one(path, force=force))
        return result_paths

    def _load_data(self):
        """Load data from the data file."""
        if not self._data_file_path.exists():
            return

        with open(self._data_file_path, "r") as f:
            data_dict = json.load(f)
            self._data = CachedData(**data_dict)
            self._data.extracted_archives = set(self._data.extracted_archives)

    def _save_data(self):
        """Save data to the data file."""
        # Ensure the parent directory exists
        self._data_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert the dataclass to a dictionary for JSON serialization
        data_dict = asdict(self._data)
        data_dict["extracted_archives"] = list(data_dict["extracted_archives"])

        with open(self._data_file_path, "w") as f:
            json.dump(data_dict, f, indent=2)

    def _get_hash_from_info(self, info: dict) -> str:
        """Calculate a hash of the info dictionary.

        Args:
            info: Dictionary containing information about the zip file

        Returns:
            str: Hash of the info dictionary
        """
        # Convert the info data to a string and hash it
        info_str = json.dumps(info, sort_keys=True)
        return hashlib.sha256(info_str.encode()).hexdigest()

    @classmethod
    def get_unique_root_dir_from_zip(cls, filepath: Path) -> str:
        """Get the unique root directory from a zip file.

        Args:
            filepath: Path to the zip file

        Returns:
            str: The root directory name

        Raises:
            ValueError: If the zip file contains more than one root directory
        """
        with zipfile.ZipFile(filepath, "r") as zf:
            # Normalize paths
            file_paths = [e.replace("\\", "/") for e in zf.namelist()]
            # Get root dirs
            root_dirs = {e.split("/")[0] for e in file_paths}

            if len(root_dirs) > 1:
                raise ValueError("The zip file contains more than one root directory.")

            # Get the only element in the set
            return root_dirs.pop()

    @classmethod
    def get_zip_path_separator(cls, filepath: Path) -> str:
        """Determine the path separator used in a zip file.

        Args:
            filepath: Path to the zip file

        Returns:
            str: The path separator used in the zip file ('/' or '\\')
        """
        with zipfile.ZipFile(filepath, "r") as zf:
            # Get a sample path from the zip
            sample_path = next(iter(zf.namelist()))
            # Check if it contains backslash
            if "\\" in sample_path:
                return "\\"
            return "/"

    def _get_info_from_zip(self, filepath: Path) -> dict:
        """Get info.json contents from a zip file, handling both forward slashes and backslashes.

        Args:
            filepath: Path to the zip file

        Returns:
            dict: Contents of info.json

        Raises:
            FileNotFoundError: If info.json is not found in the zip
            ValueError: If info.json is missing required keys
        """
        root_dir = self.get_unique_root_dir_from_zip(filepath)
        separator = self.get_zip_path_separator(filepath)

        with zipfile.ZipFile(filepath, "r") as zf:
            info_path = f"{root_dir}{separator}{FILENAME_INFO}"

            with zf.open(info_path) as info_file:
                info_data = json.load(info_file)
                return info_data

    @classmethod
    def extract_zip(cls, filepath: Path, dest: Optional[Path] = None):
        """
        Extracts a .zip archive by normalizing "/" and "\\" to be cross platform.

        Args:
            filepath: Path to the .zip file to extract.
            dest: Destination directory. Defaults to the .zip file's folder.
        """
        # Use the .zip file's directory as the destination if not provided
        dest = Path(dest) if dest else filepath.parent

        with zipfile.ZipFile(filepath, "r") as zf:
            for original_member in zf.namelist():
                # Normalize paths to handle '/' and '\' correctly
                member_normalized = original_member.replace("\\", "/")
                # Get the dest of extraction
                member_dest = dest / member_normalized

                if member_normalized.endswith("/"):
                    # If it's a folder, create it
                    member_dest.mkdir(parents=True, exist_ok=True)
                else:
                    # If it's a file extract it (the parent folder is automatically created
                    extracted_path = zf.extract(original_member, member_dest.parent)
                    # Rename to avoid having a filename with "\\" on it's name
                    Path(extracted_path).replace(
                        member_dest.parent / Path(member_normalized).name
                    )
