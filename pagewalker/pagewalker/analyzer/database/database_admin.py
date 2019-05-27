import sqlite3
import os
from os import path
from pagewalker.utilities import url_utils, time_utils, error_utils
from pagewalker import version
from pagewalker.config import config


class DatabaseAdmin(object):
    def __init__(self):
        self.page_host = url_utils.hostname_from_url(config.start_url)
        self.pages_list = self._parse_pages_list_file()
        self.conn = None

    def _parse_pages_list_file(self):
        if not config.pages_list_file:
            return False
        with open(config.pages_list_file, "r") as f:
            lines = f.readlines()
        lines = [x.strip() for x in lines]
        pages_list = []
        for line in lines:
            if line:
                if not line.startswith("/"):
                    msg = "Invalid page in '%s' file. '%s' is not starting with '/'" % (config.pages_list_file, line)
                    error_utils.exit_with_message(msg)
                pages_list.append(line)
        if not pages_list:
            error_utils.exit_with_message("File '%s' does not contain any pages" % config.pages_list_file)
        return pages_list

    def get_pages_list_count(self):
        return len(self.pages_list) if self.pages_list else 0

    def create_clean_database(self):
        self._connect_to_new_database()
        self._create_empty_tables()
        self._save_initial_config()
        self._add_first_link()
        if self.pages_list:
            self._add_links_from_list()

    def _connect_to_new_database(self):
        sqlite_file = path.join(config.current_data_dir, "data.db")
        try:
            os.remove(sqlite_file)
        except OSError:
            pass
        self.conn = sqlite3.connect(sqlite_file)

    def _create_empty_tables(self):
        schema_file = path.join(config.root, "pagewalker", "resources", "database.sql")
        with open(schema_file) as f:
            sql_data = f.read()
        c = self.conn.cursor()
        c.executescript(sql_data)
        self.conn.commit()

    def _save_initial_config(self):
        config_values = {
            "wait_time_after_load": config.wait_time_after_load,
            "max_number_pages": config.max_number_pages,
            "window_size": config.window_size,
            "headless": self._boolean_to_yes_no(config.chrome_headless),
            "chrome_timeout": config.chrome_timeout,
            "validator_enabled":  self._boolean_to_yes_no(config.validator_enabled),
            "validator_css":  self._boolean_to_yes_no(config.validator_check_css),
            "validator_warnings":  self._boolean_to_yes_no(config.validator_show_warnings),
            "scroll_after_load": self._boolean_to_yes_no(config.scroll_after_load),
            "check_external_links": self._boolean_to_yes_no(config.check_external_links),
            "check_external_links_timeout": config.check_external_links_timeout,
            "app_version": version,
            "page_start": config.start_url,
            "page_host": self.page_host,
            "time_start": time_utils.current_date_time(),
            "domain_blacklist": self._boolean_to_yes_no(config.domain_blacklist_enabled),
            "custom_cookies": self._boolean_to_yes_no(config.custom_cookies_file),
            "initial_actions": self._boolean_to_yes_no(config.initial_actions_file),
            "http_basic_auth": self._boolean_to_yes_no(config.http_basic_auth_data)
        }
        for option, value in config_values.items():
            self.add_to_config(option, value)

    def _boolean_to_yes_no(self, variable):
        return "Yes" if variable else "No"

    def _add_first_link(self):
        url = url_utils.relative_url(config.start_url)
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
