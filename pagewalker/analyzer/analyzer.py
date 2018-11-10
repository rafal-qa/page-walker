from .devtools import remote_debug, response_parser
from .database import database_admin, database_writer
from . import html_parser, links_parser, external_links, html_validator, http_headers_analyzer
from pagewalker.config import config


class Analyzer(object):
    def __init__(self):
        self.devtools_remote = remote_debug.DevtoolsRemoteDebug()
        self.validator = html_validator.HtmlValidator()
        self.db_admin = database_admin.DatabaseAdmin()
        self.external_links = external_links.ExternalLinks()

    def start_new_analysis(self):
        db_admin = self.db_admin
        db_admin.create_clean_database()
        db_connection = db_admin.get_connection()
        self.validator.set_db_connection(db_connection)
        self.external_links.set_db_connection(db_connection)

        devtools_remote = self.devtools_remote
        devtools_remote.start_session()
        self._save_chrome_version(db_admin, devtools_remote)
        db_admin.add_to_config("vnu_version", self.validator.get_vnu_version())

        if config.pages_list_file and config.pages_list_only:
            max_number_pages = db_admin.get_pages_list_count() + 1
        else:
            max_number_pages = config.max_number_pages

        for i in range(0, max_number_pages):
            next_page = db_admin.get_next_page()
            if not next_page:
                break
            self._analyze_page(next_page["id"], next_page["url"])
            self.external_links.check_links()
            self.validator.validate_if_full_queue()

        devtools_remote.end_session()
        self.validator.validate()
        db_admin.close_database()

    def _analyze_page(self, page_id, url):
        print("%s. %s" % (page_id, url))

        db_page_writer = database_writer.DatabasePageWriter(
            self.db_admin.get_connection(),
            page_id,
            url
        )
        db_page_writer.completion_status_started()

        continue_with_chrome = self._headers_analysis_before_chrome(db_page_writer, url)
        if not continue_with_chrome:
            return

        devtools_remote = self.devtools_remote
        messages = devtools_remote.open_url(url)
        if not messages:
            return

        devtools_parser = response_parser.DevtoolsResponseParser()
        devtools_parser.append_response(messages)

        if config.scroll_after_load:
            devtools_remote.scroll_to_bottom()

        messages = devtools_remote.wait(config.wait_time_after_load)
        devtools_parser.append_response(messages)

        parsed_logs = devtools_parser.get_logs()
        db_page_writer.save_devtools_data(parsed_logs)

        main_request_id = parsed_logs["general"]["main_request_id"]
        html_code = self._get_html(main_request_id)
        self._save_html_links(db_page_writer, html_code["dom"])
        self.validator.add_to_queue(db_page_writer.get_page_id(), html_code["raw"], html_code["dom"])

        db_page_writer.set_page_http_status(devtools_parser.get_main_request_http_status())
        db_page_writer.completion_status_finished()

    def _headers_analysis_before_chrome(self, db_writer, url):
        cookies_data = self.devtools_remote.get_cookies_for_url(url)
        http_headers = http_headers_analyzer.HTTPHeadersAnalyzer(config.chrome_timeout)
        url_result = http_headers.analyze_for_chrome(url, cookies_data)
        status = url_result["status"]
        if status == "ok":
            return True
        if status == "request_exception":
            db_writer.set_connection_exception(url_result["error_name"])
        elif status == "is_redirect":
            self._add_location_from_redirect(db_writer, url_result["location"])
        elif status == "is_file":
            db_writer.mark_page_as_file(url_result["content_type"], url_result["content_length"])
        db_writer.set_page_http_status(url_result["http_code"])
        db_writer.completion_status_finished()
        return False

    def _add_location_from_redirect(self, db_writer, location):
        if not location:
            return
        links = links_parser.LinksParser(db_writer.get_url())
        internal = links.filter_internal_relative([location])
        external = links.filter_external([location])
        if internal:
            db_writer.add_internal_links(internal)
        elif external:
            self.external_links.add_links(db_writer.get_page_id(), external)

    def _get_html(self, request_id):
        return {
            "raw": self.devtools_remote.get_html_raw(request_id),
            "dom": self.devtools_remote.get_html_dom()
        }

    def _save_html_links(self, db_writer, html_dom):
        html = html_parser.MyHtmlParser()
        html.feed(html_dom)
        links = links_parser.LinksParser(db_writer.get_url(), html.get_base_href())
        all_links = html.get_found_links()
        internal = links.filter_internal_relative(all_links)
        db_writer.add_internal_links(internal)
        external = links.filter_external(all_links)
        self.external_links.add_links(db_writer.get_page_id(), external)

    def _save_chrome_version(self, db_admin, devtools_remote):
        version = devtools_remote.get_version()
        db_admin.add_to_config("chrome_version", version["product"])
        db_admin.add_to_config("devtools_protocol", version["protocolVersion"])
