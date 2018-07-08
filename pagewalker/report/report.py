from os import path
from . import html_exporter


class Report(object):
    def __init__(self, sqlite_file, current_data_dir):
        self.sqlite_file = sqlite_file
        self.current_data_dir = current_data_dir

    def generate_html(self):
        html_report = html_exporter.HtmlExporter(self.sqlite_file, self.current_data_dir)
        html_report.report_pages()
        html_report.report_resources()
        html_report.report_javascript()
        html_report.report_validator()
        html_report.report_devtools()
        html_report.report_summary()
        html_report.close_db()
        self._print_confirm()

    def _print_confirm(self):
        print("-" * 50)
        print("HTML report saved to '%s' directory" % self.current_data_dir)
        print("-" * 50)

    def redirect_to_latest(self, output_data, current_subdir):
        location = "/".join([current_subdir, "report", "index.html"])
        html = "<html><head><script>window.location.replace(\"%s\");</script></head></html>" % location
        file_html = path.join(output_data, "latest_report.html")
        with open(file_html, "w") as f:
            f.write(html)
