from . import http_headers_analyzer


class ExternalLinks(object):
    def __init__(self, enabled, timeout):
        self.enabled = enabled
        self.timeout = timeout
        self.db_conn = None

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
        if not self.enabled:
            return
        links = self._get_unchecked_links()
        unchecked_count = len(links)
        if not unchecked_count:
            return
        word_link = "link" if unchecked_count == 1 else "links"
        print("[INFO] Checking %s new external %s" % (unchecked_count, word_link))
        http_headers = http_headers_analyzer.HTTPHeadersAnalyzer(self.timeout)
        for link_data in links:
            result = http_headers.analyze_for_external_links_check(link_data["url"])
            self._set_link_status(link_data["id"], result["redirect_url"], result["http_code"], result["error_name"])

    def _get_unchecked_links(self):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id, url FROM external_links_url WHERE checked IS NULL"
        )
        result = c.fetchall()
        links = []
        for row in result:
            link_id, url = row
            record = {
                "id": link_id,
                "url": url
            }
            links.append(record)
        return links

    def _set_link_status(self, link_id, redirect_url, http_status, error_name):
        c = self.db_conn.cursor()
        c.execute(
            "UPDATE external_links_url SET checked = 1, "
            "redirect_url = ?, http_status = ?, exception_name = ? WHERE id = ?",
            (redirect_url, http_status, error_name, link_id)
        )
        self.db_conn.commit()
