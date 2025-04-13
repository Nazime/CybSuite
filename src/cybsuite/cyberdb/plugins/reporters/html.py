import base64
from pathlib import Path

from cybsuite.cyberdb.bases import BaseReporter
from cybsuite.cyberdb.consts import PATH_TEMPLATES
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from koalak.plugin_manager import Metadata

# HTML Report paths
PATH_HTML_REPORT = PATH_TEMPLATES / "html_report"
PATH_HTML_TEMPLATE = PATH_HTML_REPORT / "main.html"


class HtmlReporter(BaseReporter):
    name = "html"
    metadata = Metadata(
        category="reporters",
        description="Generate HTML report with DataTables for controls",
    )
    extension = ".html"

    def configure(self, latest_run=None):
        self.latest_run = latest_run

    def run(self, output):
        from cybsuite.cyberdb import pm_reporter

        json_reporter = pm_reporter["controls_json"](self.cyberdb)
        json_reporter.configure(latest_run=self.latest_run)
        data = json_reporter.do_processing()

        # Prepare context for all templates
        context = {
            "controls": data["controls"],
            "observations": data["observations"],
            "summary": data["summary"],
        }

        # Create Jinja2 environment with base64 filter and file loader
        env = Environment(
            undefined=StrictUndefined, loader=FileSystemLoader(PATH_HTML_REPORT)
        )

        # Add base64_file filter for file encoding
        def base64_file(file_path):
            return base64.b64encode((PATH_HTML_REPORT / file_path).read_bytes()).decode(
                "utf-8"
            )

        env.filters["base64_file"] = base64_file

        # Create a Jinja2 Template object and render the HTML content
        with open(PATH_HTML_TEMPLATE) as f:
            template = env.from_string(f.read())
        html_report = template.render(**context)

        # Save the generated HTML report to a file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as file:
            file.write(html_report)
