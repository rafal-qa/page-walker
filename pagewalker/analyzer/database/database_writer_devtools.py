from pagewalker.utilities import url_utils, time_utils


class DatabasePageWriterDevtools(object):
    def __init__(self, db_connection, page_id, url):
        self.conn = db_connection
        self.page_id = page_id
        self.url = url

    def general(self, logs_general):
        time_dom_content = time_utils.time_diff_ms(logs_general["time_start"], logs_general["time_dom_content"])
        time_load = time_utils.time_diff_ms(logs_general["time_start"], logs_general["time_load"])
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO pages_stat (page_id, time_dom_content, time_load) VALUES (?, ?, ?)",
            (self.page_id, time_dom_content, time_load)
        )

    def network_requests(self, logs_network_requests, time_start_page):
        for request_data in logs_network_requests:
            self._network_request(request_data, time_start_page)

    def _network_request(self, request, time_start_page):
        url_orig = request["resource_url"]
        if not url_utils.has_valid_scheme(url_orig, ["http", "https"]):
            return
        url_truncated = url_utils.trim_url(url_orig)
        is_truncated = 0 if url_truncated == url_orig else 1
        resource_id = self._get_resource_id(url_truncated, is_truncated)
        http_status = request["http_status"]
        error_id = self._get_error_id(request["error_name"]) if not http_status else None
        time_started = time_utils.time_diff_ms(time_start_page, request["time_start"])
        time_load = time_utils.time_diff_ms(request["time_start"], request["time_end"])
        is_main = 1 if "is_main_resource" in request else 0
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO devtools_request "
            "(page_id, resource_id, error_id, http_status, from_cache, data_received, "
            "time_started, time_load, is_main) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.page_id, resource_id, error_id, http_status, request["from_cache"], request["data_received"],
             time_started, time_load, is_main)
        )

    def _get_resource_id(self, url, is_truncated):
        page_host = url_utils.hostname_from_url(self.url)
        relative_url = url_utils.internal_relative_url(url, page_host)
        if relative_url is False:
            is_external = 1
        else:
            url = relative_url
            is_external = 0

        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM devtools_resource WHERE url = ? AND is_truncated = ? AND is_external = ?",
            (url, is_truncated, is_external)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO devtools_resource (url, is_truncated, is_external) VALUES (?, ?, ?)",
            (url, is_truncated, is_external)
        )
        return c.lastrowid

    def _get_error_id(self, error_name):
        if not error_name:
            return None
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM devtools_request_error WHERE name = ?", (error_name,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO devtools_request_error (name) VALUES (?)", (error_name,)
        )
        return c.lastrowid

    def runtime_exceptions(self, logs_runtime_exceptions):
        c = self.conn.cursor()
        for description in logs_runtime_exceptions:
            exception_id = self._get_exception_id(description)
            c.execute(
                "INSERT INTO devtools_js_exception (page_id, exception_id) VALUES (?, ?)", (self.page_id, exception_id)
            )

    def _get_exception_id(self, description):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM devtools_js_exception_text WHERE description = ?", (description,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO devtools_js_exception_text (description) VALUES (?)", (description,)
        )
        return c.lastrowid

    def console_logs(self, logs):
        for log_data in logs:
            self._save_log_entry(log_data)

    def _save_log_entry(self, log_data):
        if not self._wanted_log(log_data["level"], log_data["source"]):
            return
        log_id = self._get_log_id(log_data)
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO devtools_console (page_id, log_id) VALUES (?, ?)", (self.page_id, log_id)
        )

    # network errors are processed separately
    def _wanted_log(self, level, source):
        return level in ["warning", "error"] and source not in ["network"]

    def _get_log_id(self, log_data):
        log_levels = {
            "verbose": 1,
            "info": 2,
            "warning": 3,
            "error": 4
        }
        log_sources = {
            "xml": 1,
            "javascript": 2,
            "network": 3,
            "storage": 4,
            "appcache": 5,
            "rendering": 6,
            "security": 7,
            "deprecation": 8,
            "worker": 9,
            "violation": 10,
            "intervention": 11,
            "recommendation": 12,
            "other": 13
        }
        level = log_data["level"]
        level_id = log_levels[level] if level in log_levels else 0
        source = log_data["source"]
        source_id = log_sources[source] if source in log_sources else 0
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM devtools_console_log WHERE level_id = ? AND source_id = ? AND description = ?",
            (level_id, source_id, log_data["text"])
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO devtools_console_log (level_id, source_id, description) VALUES (?, ? ,?)",
            (level_id, source_id, log_data["text"])
        )
        return c.lastrowid
