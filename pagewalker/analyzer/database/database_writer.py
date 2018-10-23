from . import database_writer_devtools


class DatabasePageWriter(object):
    def __init__(self, db_connection, page_id, url):
        self.conn = db_connection
        self.page_id = page_id
        self.url = url

    def get_page_id(self):
        return self.page_id

    def get_url(self):
        return self.url

    def completion_status_started(self):
        self._change_status(2)

    def completion_status_finished(self):
        self._change_status(1)

    def _change_status(self, status_code):
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET completion_status = ? WHERE id = ?", (status_code, self.page_id)
        )
        self.conn.commit()

    def set_connection_exception(self, error_name):
        exception_id = self._get_connection_exception_id(error_name)
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET exception_id = ? WHERE id = ?", (exception_id, self.page_id)
        )
        self.conn.commit()

    def _get_connection_exception_id(self, error_name):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM pages_connection_exception WHERE name = ?", (error_name,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO pages_connection_exception (name) VALUES (?)", (error_name,)
        )
        return c.lastrowid

    def mark_page_as_file(self, content_type, content_length):
        type_id = self._get_file_type_id(content_type)
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET file_type = ? WHERE id = ?", (type_id, self.page_id)
        )
        c.execute(
            "INSERT INTO pages_stat (page_id, file_content_length) VALUES (?, ?)", (self.page_id, content_length)
        )
        self.conn.commit()

    def _get_file_type_id(self, content_type):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM pages_file_type WHERE content_type = ?", (content_type,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO pages_file_type (content_type) VALUES (?)", (content_type,)
        )
        return c.lastrowid

    def add_internal_links(self, relative_links):
        for link in relative_links:
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
                "INSERT INTO pages (parent_id, url, completion_status, file_type) VALUES (?,?,?,?)",
                (parent_id, link, 0, 0)
            )
            self.conn.commit()

    def set_page_http_status(self, http_status):
        c = self.conn.cursor()
        c.execute(
            "UPDATE pages SET http_status = ? WHERE id = ?", (http_status, self.page_id)
        )
        self.conn.commit()

    def save_devtools_data(self, logs):
        database_devtools = database_writer_devtools.DatabasePageWriterDevtools(
            self.conn, self.page_id, self.url
        )
        database_devtools.general(logs["general"])
        database_devtools.network_requests(logs["network_requests"], logs["general"]["time_start"])
        database_devtools.runtime_exceptions(logs["runtime_exceptions"])
        database_devtools.console_logs(logs["console_logs"])
        self.conn.commit()
