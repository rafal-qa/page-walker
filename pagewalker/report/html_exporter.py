import json
from .database import database_reader
from . import html_exporter_files
from . import report_utils as utils


class HtmlExporter(object):
    def __init__(self, sqlite_file, current_data_dir):
        self.db = database_reader.DatabaseReader(sqlite_file)
        files = html_exporter_files.HtmlExporterFiles(current_data_dir)
        files.prepare_directory()
        self.files = files
        self.error_counts = {}

    def report_pages(self):
        pages_list = self.db.page_data.pages_list_with_data()
        requests_stats = self.db.page_data.request_stats_for_pages()
        counts = {
            "pages": 0,
            "files": 0,
            "failed": 0,
            "requests_total_list": [],
            "load_time_list": []
        }
        data_pages = []
        for row in pages_list:
            single_page = self._single_page_data(row, requests_stats)
            self._update_page_counts(counts, single_page)
            data_pages.append(single_page)

        stat = {
            "pages": counts["pages"],
            "files": counts["files"],
            "failed": counts["failed"],
            "requests_per_page": utils.list_average_as_int(counts["requests_total_list"]),
            "load_time": utils.list_average_as_int(counts["load_time_list"])
        }

        data_order = (
            "id", "url", "file_content_type", "file_content_length", "time_load", "http_status", "exception_name",
            "requests_count", "requests_cached_percent", "data_received_sum"
        )
        data_simplified = utils.convert_dict_to_list(data_pages, data_order)

        save_data = {
            "head": data_order,
            "main": data_simplified,
            "stat": stat
        }

        self.error_counts["pages"] = stat["failed"]
        self.files.save_json(save_data, "pages")

    def _single_page_data(self, row, requests_stats):
        page_id = row["id"]
        stats = requests_stats[page_id] if page_id in requests_stats else {}
        requests_count = stats["requests_count"] if "requests_count" in stats else 0
        from_cache = stats["from_cache"] if "from_cache" in stats else 0
        requests_cached_percent = utils.percent(from_cache, requests_count)
        data_received = stats["data_received"] if "data_received" in stats else 0
        file_content_length = row["file_content_length"]
        if file_content_length is not None:
            file_content_length = utils.bytes_to_kilobytes_as_int(file_content_length)

        return {
            "id": page_id,
            "url": row["url"],
            "file_content_type": row["file_content_type"],
            "file_content_length": file_content_length,
            "time_load": row["time_load"],
            "http_status": row["http_status"],
            "exception_name": row["exception_name"],
            "requests_count": requests_count,
            "requests_cached_percent": requests_cached_percent,
            "data_received_sum": utils.bytes_to_kilobytes_as_int(data_received)
        }

    def _update_page_counts(self, counts, data):
        if data["file_content_type"]:
            counts["files"] += 1
        else:
            counts["pages"] += 1
            if data["http_status"]:
                counts["requests_total_list"].append(data["requests_count"])
                if data["time_load"] is not None:
                    counts["load_time_list"].append(data["time_load"])
            if not data["http_status"] or data["http_status"] >= 400:
                counts["failed"] += 1

    def report_resources(self):
        resources_list = self.db.resource_data.resource_list_only()
        resources_stat = self.db.resource_data.request_stat_for_resources()
        resources_error = self.db.resource_data.request_error_for_resources()
        counts = {
            "error_internal": 0,
            "error_external": 0,
            "requests_internal": 0,
            "requests_external": 0,
            "requests_cached": 0
        }
        data_resources = []
        for row in resources_list:
            single_resource = self._single_resource_data(row, resources_stat, resources_error)
            self._update_resource_counts(counts, single_resource)
            data_resources.append(single_resource)

        stat_requests_all = counts["requests_internal"] + counts["requests_external"]
        stat = {
            "error_internal": counts["error_internal"],
            "error_external": counts["error_external"],
            "cached_percent": utils.percent(counts["requests_cached"], stat_requests_all, True),
            "external_percent": utils.percent(counts["requests_external"], stat_requests_all, True)
        }

        data_order = (
            "id", "url", "is_truncated", "is_external",
            "requests_all", "requests_errors", "requests_cached_percent", "requests_unfinished_percent",
            "avg_size", "avg_load_time", "pages_with_error"
        )
        data_simplified = utils.convert_dict_to_list(data_resources, data_order)

        save_data = {
            "head": data_order,
            "main": data_simplified,
            "stat": stat
        }

        self.error_counts["resources"] = stat["error_internal"] + stat["error_external"]
        self.files.save_json(save_data, "resources")

    def _single_resource_data(self, row, resources_stat, resources_error):
        resource_id = row["id"]
        is_external = row["is_external"]
        stats = resources_stat[resource_id]

        requests_finished = stats["requests_finished"] if "requests_finished" in stats else 0
        requests_unfinished = stats["requests_unfinished"] if "requests_unfinished" in stats else 0
        requests_all = requests_finished + requests_unfinished

        from_cache = stats["from_cache"] if "from_cache" in stats else 0
        requests_cached_percent = utils.percent(from_cache, requests_finished)
        requests_unfinished_percent = utils.percent(requests_unfinished, requests_all)

        avg_size = stats["avg_size"] if "avg_size" in stats else 0
        avg_load_time = stats["avg_load_time"] if "avg_load_time" in stats else 0
        avg_load_time = int(round(avg_load_time))

        error = resources_error[resource_id] if resource_id in resources_error else {}
        requests_errors = error["requests_errors"] if "requests_errors" in error else 0
        pages_with_error = error["pages_with_error"] if "pages_with_error" in error else None

        return {
            "id": resource_id,
            "url": row["url"],
            "is_truncated": row["is_truncated"],
            "is_external": is_external,
            "requests_all": requests_all,
            "requests_errors": requests_errors,
            "from_cache": from_cache,
            "requests_cached_percent": requests_cached_percent,
            "requests_unfinished_percent": requests_unfinished_percent,
            "avg_size": utils.bytes_to_kilobytes_as_int(avg_size),
            "avg_load_time": avg_load_time,
            "pages_with_error": pages_with_error
        }

    def _update_resource_counts(self, counts, data):
        if data["requests_errors"]:
            if data["is_external"]:
                counts["error_external"] += 1
            else:
                counts["error_internal"] += 1

        if data["is_external"]:
            counts["requests_external"] += data["requests_all"]
        else:
            counts["requests_internal"] += data["requests_all"]

        if data["from_cache"]:
            counts["requests_cached"] += 1

    def report_javascript(self):
        exceptions = self.db.javascript_data.exception_list()
        pages = self.db.javascript_data.pages_for_exception()
        data_exceptions = []
        for log in exceptions:
            exception_id = log["id"]
            pages_with_error = pages[exception_id] if exception_id in pages else None
            single_exception = {
                "id": exception_id,
                "occurrences": log["occurrences"],
                "description": log["description"],
                "pages_with_error": pages_with_error
            }
            data_exceptions.append(single_exception)

        stat = {
            "exception": len(exceptions)
        }

        data_order = ("id", "occurrences", "description", "pages_with_error")
        data_simplified = utils.convert_dict_to_list(data_exceptions, data_order)

        save_data = {
            "head": data_order,
            "main": data_simplified,
            "stat": stat
        }

        self.error_counts["javascript"] = stat["exception"]
        self.files.save_json(save_data, "javascript")

    def report_devtools(self):
        logs = self.db.devtools_data.log_list()
        pages = self.db.devtools_data.pages_for_log()
        counts = {
            "error_sum": 0,
            "warning_sum": 0
        }
        data_devtools = []
        for log in logs:
            log_id = log["id"]
            level_id = log["level_id"]
            single_devtools = {
                "id": log_id,
                "occurrences": log["occurrences"],
                "level_id": level_id,
                "source_id": log["source_id"],
                "description": log["description"],
                "pages_with_log": pages[log_id] if log_id in pages else None
            }
            data_devtools.append(single_devtools)

            if level_id == 4:
                counts["error_sum"] += 1
            elif level_id == 3:
                counts["warning_sum"] += 1

        stat = {
            "error": counts["error_sum"],
            "warning": counts["warning_sum"]
        }

        data_order = ("id", "occurrences", "level_id", "source_id", "description", "pages_with_log")
        data_simplified = utils.convert_dict_to_list(data_devtools, data_order)

        save_data = {
            "head": data_order,
            "main": data_simplified,
            "stat": stat
        }

        self.error_counts["devtools"] = stat["error"]
        self.files.save_json(save_data, "devtools")

    def report_validator(self):
        html_raw_list = self.db.validator_data.messages(1)
        html_dom_list = self.db.validator_data.messages(2)
        main_extract_raw = self.db.validator_data.top_extract_for_message(1)
        main_extract_dom = self.db.validator_data.top_extract_for_message(2)
        details_raw = self.db.validator_data.extracts_and_pages_for_message(1)
        details_dom = self.db.validator_data.extracts_and_pages_for_message(2)
        messages_in_raw_html = []
        counts = {
            "occurrences_all": 0,
            "errors_raw": 0,
            "errors_dom": 0
        }
        data_validator = []
        for row in html_raw_list:
            single_validator_raw = self._single_validator_html_raw(row, main_extract_raw, details_raw)
            data_validator.append(single_validator_raw)
            messages_in_raw_html.append(single_validator_raw["id"])
            if single_validator_raw["is_error"]:
                counts["occurrences_all"] += single_validator_raw["occurrences"]
                counts["errors_raw"] += 1

        # don't save duplicates - save only "dom" errors not present on "raw"
        # every message_id is only in one of HTML types: raw or dom
        for row in html_dom_list:
            if row["message_id"] not in messages_in_raw_html:
                single_validator_dom = self._single_validator_html_dom(row, main_extract_dom, details_dom)
                data_validator.append(single_validator_dom)
                if single_validator_dom["is_error"]:
                    counts["occurrences_all"] += single_validator_dom["occurrences"]
                    counts["errors_dom"] += 1

        stat = {
            "errors_raw": counts["errors_raw"],
            "errors_dom": counts["errors_dom"],
            "occurrences_all": counts["occurrences_all"]
        }

        data_order = ("id", "html_type", "message", "extract", "occurrences", "is_error", "details")
        data_simplified = utils.convert_dict_to_list(data_validator, data_order)

        save_data = {
            "head": data_order,
            "main": data_simplified,
            "stat": stat
        }

        self.error_counts["validator"] = stat["errors_raw"] + stat["errors_dom"]
        self.files.save_json(save_data, "validator")

    def _single_validator_html_raw(self, row, main_extract, details):
        message_id = row["message_id"]
        extract = json.loads(main_extract[message_id]) if message_id in main_extract else ""
        details = details[message_id] if message_id in details else None
        return {
            "id": message_id,
            "html_type": 1,
            "message": row["message"],
            "extract": extract,
            "occurrences": row["occurrences"],
            "is_error": row["is_error"],
            "details": details
        }

    def _single_validator_html_dom(self, row, main_extract, details):
        message_id = row["message_id"]
        extract = json.loads(main_extract[message_id]) if message_id in main_extract else ""
        details = details[message_id] if message_id in details else None
        return {
            "id": message_id,
            "html_type": 2,
            "message": row["message"],
            "extract": extract,
            "occurrences": row["occurrences"],
            "is_error": row["is_error"],
            "details": details
        }

    def report_summary(self):
        stat = self.db.general_data.summary()
        stat["unique_errors"] = sum(self.error_counts.values())
        stat["data_total"] = utils.bytes_to_megabytes_as_string(stat["data_total"])
        save_data = {
            "config": self.db.general_data.config_data(),
            "error": self.error_counts,
            "stat": stat
        }
        self.files.save_json(save_data, "summary")

    def close_db(self):
        self.db.close()
