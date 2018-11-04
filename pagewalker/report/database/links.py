
class DatabaseLinks(object):
    def __init__(self, conn):
        self.conn = conn

    def link_list(self):
        c = self.conn.cursor()
        c.execute("""
            SELECT L.link_id, COUNT(*), U.url, U.redirect_url, U.http_status, U.exception_name
            FROM external_links AS L
            JOIN external_links_url AS U
                ON L.link_id = U.id
            GROUP BY L.link_id
        """)
        result = c.fetchall()
        data_links = []
        for row in result:
            link_id, occurrences, url, redirect_url, http_status, exception_name = row
            one_link_data = {
                "id": link_id,
                "occurrences": occurrences,
                "url": url,
                "redirect_url": redirect_url,
                "http_status": http_status,
                "exception_name": exception_name
            }
            data_links.append(one_link_data)
        return data_links

    def pages_with_link(self):
        max_pages_on_list = 10
        c = self.conn.cursor()
        c.execute(
            "SELECT DISTINCT page_id, link_id FROM external_links ORDER BY page_id"
        )
        result = c.fetchall()
        data_links = {}
        for row in result:
            page_id, link_id = row
            if link_id not in data_links:
                data_links[link_id] = []
            if len(data_links[link_id]) < max_pages_on_list:
                data_links[link_id].append(page_id)
        return data_links
