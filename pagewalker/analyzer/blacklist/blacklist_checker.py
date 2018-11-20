from pagewalker.utilities import url_utils, error_utils
from pagewalker.config import config


class BlacklistChecker(object):
    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.blacklist = self._load_blacklist()

    def _load_blacklist(self):
        try:
            with open(config.domain_blacklist_file, "r") as f:
                lines = f.readlines()
        except IOError:
            return []
        lines = [x.strip() for x in lines]
        return lines

    def check(self):
        if not self.blacklist:
            error_utils.show_warning("Domain blacklist is empty or file is not readable")
            return
        self._check_resources()
        self._check_external_links()

    def _check_resources(self):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id, url FROM devtools_resource WHERE is_external = 1"
        )
        result = c.fetchall()
        for row in result:
            url_id, url = row
            c.execute(
                "UPDATE devtools_resource SET url_blacklisted = ? WHERE id = ?", (self._is_blacklisted(url), url_id)
            )
        self.db_conn.commit()

    def _check_external_links(self):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id, url, redirect_url FROM external_links_url"
        )
        result = c.fetchall()
        for row in result:
            url_id, url, redirect_url = row
            c.execute(
                "UPDATE external_links_url SET url_blacklisted = ? WHERE id = ?", (self._is_blacklisted(url), url_id)
            )
            if redirect_url:
                c.execute(
                    "UPDATE external_links_url SET redirect_url_blacklisted = ? WHERE id = ?",
                    (self._is_blacklisted(redirect_url), url_id)
                )
        self.db_conn.commit()

    def _is_blacklisted(self, url):
        for subdomain in url_utils.all_level_subdomains(url):
            if subdomain in self.blacklist:
                return True
        return False
