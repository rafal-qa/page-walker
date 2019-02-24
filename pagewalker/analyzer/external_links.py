from multiprocessing.dummy import Pool as ThreadPool
from . import http_headers_analyzer
from pagewalker.config import config


class ExternalLinks(object):
    def __init__(self):
        self.db_conn = None
        self.links_status_to_save = {}

    def set_db_connection(self, db_connection):
        self.db_conn = db_connection

    def add_links(self, page_id, links):
        for url in links:
            self._add_single_link(page_id, url)

    def _add_single_link(self, page_id, url):
        c = self.db_conn.cursor()
        link_id = self._get_single_link_id(url)
        c.execute(
            "INSERT INTO external_links (page_id, link_id) VALUES (?,?)", (page_id, link_id)
        )
        self.db_conn.commit()

    def _get_single_link_id(self, url):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id FROM external_links_url WHERE url = ?", (url,)
        )
        result = c.fetchone()
        if result:
            return result[0]
        c.execute(
            "INSERT INTO external_links_url (url) VALUES (?)", (url,)
        )
        return c.lastrowid

    def check_links(self):
        if not config.check_external_links:
            return
        links_data = self._get_unchecked_links()
        unchecked_count = len(links_data)
        if not unchecked_count:
            return
        word_link = "link" if unchecked_count == 1 else "links"
        print("[INFO] Checking %s new external %s in max. %s threads" %
              (unchecked_count, word_link, config.check_external_links_threads))
        self._check_links_in_threads(links_data)
        self._set_links_status()

    def _get_unchecked_links(self):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id, url FROM external_links_url WHERE checked IS NULL"
        )
        result = c.fetchall()
        links_data = []
        for row in result:
            link_id, url = row
            record = {
                "id": link_id,
                "url": url
            }
            links_data.append(record)
        return links_data

    def _check_links_in_threads(self, links_data):
        pool = ThreadPool(config.check_external_links_threads)
        pool.map(self._check_single_link, links_data)
        pool.close()
        pool.join()

    def _check_single_link(self, link_data):
        http_headers = http_headers_analyzer.HTTPHeadersAnalyzer(config.check_external_links_timeout)
        link_id = link_data["id"]
        self.links_status_to_save[link_id] = http_headers.analyze_for_external_links_check(link_data["url"])

    def _set_links_status(self):
        c = self.db_conn.cursor()
        for link_id, link_data in self.links_status_to_save.items():
            c.execute(
                "UPDATE external_links_url SET checked = 1, "
                "redirect_url = ?, http_status = ?, exception_name = ? WHERE id = ?",
                (link_data["redirect_url"], link_data["http_code"], link_data["error_name"], link_id)
            )
        self.db_conn.commit()
        self.links_status_to_save = {}
