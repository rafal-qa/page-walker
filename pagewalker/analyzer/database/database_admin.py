import sqlite3
import os
from pagewalker.utilities import url_utils, time_utils, error_utils
from pagewalker import version


class DatabaseAdmin(object):
    def __init__(self, page_start, sqlite_file, pages_list_file, config_to_save):
        self.page_start = page_start
        self.page_host = url_utils.hostname_from_url(page_start)
        self.sqlite_file = sqlite_file
        self.pages_list = self._parse_pages_list_file(pages_list_file) if pages_list_file else False
        self.config_to_save = config_to_save
        self.conn = None

    def _parse_pages_list_file(self, file_name):
        try:
            with open(file_name, "r") as f:
                lines = f.readlines()
        except IOError:
            error_utils.exit_with_message("Unable to open file '%s'" % file_name)
            return
        lines = [x.strip() for x in lines]
        pages_list = []
        for line in lines:
            if line:
                if not line.startswith("/"):
                    msg = "Invalid page in '%s' file. '%s' is not starting with '/'" % (file_name, line)
                    error_utils.exit_with_message(msg)
                pages_list.append(line)
        if not pages_list:
            error_utils.exit_with_message("File '%s' does not contain any pages" % file_name)
        return pages_list

    def get_pages_list_count(self):
        return len(self.pages_list) if self.pages_list else 0

    def create_clean_database(self):
        self._connect_to_new_database(self.sqlite_file)
        self._create_empty_tables()
        self._save_initial_config()
        self._add_first_link()
        if self.pages_list:
            self._add_links_from_list()

    def _connect_to_new_database(self, sqlite_file):
        try:
            os.remove(sqlite_file)
        except OSError:
            pass
        self.conn = sqlite3.connect(sqlite_file)

    def _create_empty_tables(self):
        schema_file = os.path.join("lib", "pagewalker", "database.sql")
        with open(schema_file) as f:
            sql_data = f.read()
        c = self.conn.cursor()
        c.executescript(sql_data)
        self.conn.commit()

    def _save_initial_config(self):
        config_values = self.config_to_save
        config_values["app_version"] = version
        config_values["page_start"] = self.page_start
        config_values["page_host"] = self.page_host
        config_values["time_start"] = time_utils.current_date_time()
        for option, value in config_values.items():
            self.add_to_config(option, value)

    def _add_first_link(self):
        url = url_utils.relative_url(self.page_start)
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO pages (parent_id, url, completion_status, file_type) VALUES (?, ?, ?, ?)", (0, url, 0, 0)
        )
        self.conn.commit()

    def _add_links_from_list(self):
        c = self.conn.cursor()
        for url in self.pages_list:
            c.execute(
                "INSERT INTO pages (parent_id, url, completion_status, file_type) VALUES (?, ?, ?, ?)", (0, url, 0, 0)
            )
        self.conn.commit()

    def get_connection(self):
        return self.conn

    def add_to_config(self, option, value):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO config (option, value) VALUES (?, ?)", (option, value)
        )
        self.conn.commit()

    def close_database(self):
        config_values = {
            "unvisited_pages": self._get_unvisited_pages_count(),
            "time_end": time_utils.current_date_time()
        }
        for option, value in config_values.items():
            self.add_to_config(option, value)
        self.conn.close()

    def _get_unvisited_pages_count(self):
        c = self.conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM pages WHERE completion_status = 0"
        )
        return c.fetchone()[0]

    def get_next_page(self):
        c = self.conn.cursor()
        c.execute(
            "SELECT id, url FROM pages WHERE completion_status = 0 ORDER BY id LIMIT 1"
        )
        result = c.fetchone()
        if not result:
            return False
        page_id, relative_url = result
        absolute_url = self.page_host + relative_url
        return {
            "id": page_id,
            "url": absolute_url
        }
