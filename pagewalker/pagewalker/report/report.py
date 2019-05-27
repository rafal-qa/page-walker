from os import path
from . import html_exporter
from pagewalker.config import config


class Report(object):
    def generate_html(self):
        html_report = html_exporter.HtmlExporter()
        html_report.report_pages()
        html_report.report_resources()
        html_report.report_javascript()
        html_report.report_console()
        html_report.report_links()
        html_report.report_validator()
        html_report.report_summary()
        html_report.close_db()
        self._print_confirm()
        self._redirect_to_latest()

    def _print_confirm(self):
        print("")
        print("-" * 50)
        print("HTML report was saved to: %s" % path.join(config.current_data_dir, "report", "index.html"))
        print("-" * 50)

    def _redirect_to_latest(self):
        location = "/".join([config.current_data_subdir, "report", "index.html"])
        html = "<html><head><script>window.location.replace(\"%s\");</script></head></html>" % location
        file_html = path.join(config.output_data, "latest_report.html")
        with open(file_html, "w") as f:
            f.write(html)
