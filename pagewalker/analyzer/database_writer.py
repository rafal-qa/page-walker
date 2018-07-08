from pagewalker.utilities import url_utils, time_utils


class DatabasePageWriter(object):
    def __init__(self, db_connection, page_id, url):
        self.conn = db_connection
        self.page_id = page_id
        self.url = url
        self.page_host = url_utils.hostname_from_url(url)

    def get_page_id(self):
        return self.page_id

    def get_url(self):
        return self.url

    def change_status_started(self):
        self._change_status(2)

    def change_status_finished(self, error_name=None):
        if error_name:
            self._set_connection_exception(error_name)
        self._change_status(1)

    def _change_status(self, status_code):
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET status = ? WHERE id = ?", (status_code, self.page_id)
        )
        self.conn.commit()

    def _set_connection_exception(self, error_name):
        exception_id = self._get_connection_exception_id(error_name)
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET exception_id = ? WHERE id = ?", (exception_id, self.page_id)
        )
        self.conn.commit()

    def _get_connection_exception_id(self, error_name):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM connection_exceptions WHERE name = ?", (error_name,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO connection_exceptions (name) VALUES (?)", (error_name,)
        )
        return c.lastrowid

    def add_internal_links(self, links):
        for link in links:
            self._add_page_if_not_exists(link)

    def _add_page_if_not_exists(self, link):
        c = self.conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM pages WHERE url = ?", (link,)
        )
        count = c.fetchone()[0]
        if count == 0:
            parent_id = self.page_id
            c.execute(
                "INSERT INTO pages (parent_id, url, status, file_type) VALUES (?,?,?,?)", (parent_id, link, 0, 0)
            )
            self.conn.commit()

    def save_page_as_file(self, content_type, content_length):
        type_id = self._get_file_type_id(content_type)
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET file_type = ? WHERE id = ?", (type_id, self.page_id)
        )
        c.execute(
            "INSERT INTO pages_stats (page_id, file_content_length) VALUES (?, ?)", (self.page_id, content_length)
        )
        self.conn.commit()

    def _get_file_type_id(self, content_type):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM file_types WHERE content_type = ?", (content_type,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO file_types (content_type) VALUES (?)", (content_type,)
        )
        return c.lastrowid

    def save_devtools_data(self, logs):
        if len(logs["general"]):
            self._save_devtools_general(logs["general"])

        if len(logs["network_requests"]):
            time_start_page = logs["general"]["time_start"] if "time_start" in logs["general"] else None
            self._save_devtools_network_requests(logs["network_requests"], time_start_page)

        if len(logs["runtime_exceptions"]):
            self._save_devtools_runtime_exceptions(logs["runtime_exceptions"])

        if len(logs["other_logs"]):
            self._save_devtools_other_logs(logs["other_logs"])

    def _save_devtools_general(self, logs_general):
        time_dom_content = time_utils.time_diff_ms(logs_general["time_start"], logs_general["time_dom_content"])
        time_load = time_utils.time_diff_ms(logs_general["time_start"], logs_general["time_load"])
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO pages_stats (page_id, time_dom_content, time_load) VALUES (?, ?, ?)",
            (self.page_id, time_dom_content, time_load)
        )
        self.conn.commit()

    def _save_devtools_network_requests(self, logs_network_requests, time_start_page):
        c = self.conn.cursor()
        for request in logs_network_requests.values():
            http_status = request["http_status"]
            from_cache = request["from_cache"]
            data_received = request["data_received"]
            resource_id = self._get_resource_id(request["url"], request["url_is_truncated"])
            error_id = self._get_error_id(request["error_name"]) if not http_status else None
            time_started = time_utils.time_diff_ms(time_start_page, request["time_start"])
            time_load = time_utils.time_diff_ms(request["time_start"], request["time_end"])
            is_main = 1 if "is_main_resource" in request else 0
            c.execute(
                "INSERT INTO requests "
                "(page_id, resource_id, error_id, http_status, from_cache, data_received, "
                "time_started, time_load, is_main) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.page_id, resource_id, error_id, http_status, from_cache, data_received,
                 time_started, time_load, is_main)
            )
        self.conn.commit()

    def _get_resource_id(self, url, is_truncated):
        relative_url = url_utils.internal_relative_url(url, self.page_host)
        if relative_url is False:
            is_external = 1
        else:
            url = relative_url
            is_external = 0

        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM resources WHERE url = ? AND is_truncated = ? AND is_external = ?",
            (url, is_truncated, is_external)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO resources (url, is_truncated, is_external) VALUES (?, ?, ?)",
            (url, is_truncated, is_external)
        )
        return c.lastrowid

    def _get_error_id(self, error_name):
        if not error_name:
            return None
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM requests_error WHERE name = ?", (error_name,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO requests_error (name) VALUES (?)", (error_name,)
        )
        return c.lastrowid

    def _save_devtools_runtime_exceptions(self, logs_runtime_exceptions):
        c = self.conn.cursor()
        for description in logs_runtime_exceptions:
            exception_id = self._get_exception_id(description)
            c.execute(
                "INSERT INTO pages_js_exceptions (page_id, exception_id) VALUES (?, ?)", (self.page_id, exception_id)
            )
        self.conn.commit()

    def _get_exception_id(self, description):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM js_exceptions WHERE description = ?", (description,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO js_exceptions (description) VALUES (?)", (description,)
        )
        return c.lastrowid

    def _save_devtools_other_logs(self, other_logs):
        c = self.conn.cursor()
        for log in other_logs:
            if self._is_wanted_log(log["level_id"], log["source_id"]):
                log_id = self._get_log_id(log["level_id"], log["source_id"], log["text"])
                c.execute(
                    "INSERT INTO pages_devtools_logs (page_id, log_id) VALUES (?, ?)", (self.page_id, log_id)
                )
        self.conn.commit()

    # only warning/error
    # network errors are processed separately
    def _is_wanted_log(self, level_id, source_id):
        return level_id in [3, 4] and source_id != 3

    def _get_log_id(self, level_id, source_id, description):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM devtools_logs WHERE level_id = ? AND source_id = ? AND description = ?",
            (level_id, source_id, description)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO devtools_logs (level_id, source_id, description) VALUES (?, ? ,?)",
            (level_id, source_id, description)
        )
        return c.lastrowid
