from pagewalker.utilities import url_utils

try:
    from html.parser import HTMLParser  # Python 3
except ImportError:
    from HTMLParser import HTMLParser  # Python 2


class MyHtmlParser(HTMLParser):
    def __init__(self, base_url):
        HTMLParser.__init__(self)
        self.base_url = base_url
        self.base_url_host = url_utils.hostname_from_url(base_url)
        self.base_href = None
        self.all_links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            link = dict(attrs).get("href")
            if link:
                self.all_links.append(link.strip())
        if tag == "base" and not self.base_href:
            link = dict(attrs).get("href")
            if link:
                self.base_href = link.strip()

    def get_links(self):
        links = {
            "internal": [],
            "external": []
        }
        for link in self._get_unique_links():
            if self._is_link_valid(link):
                link_data = self._analyze_link(link)
                link_type = link_data["type"]
                links[link_type].append(link_data["link"])
        return links

    def _get_unique_links(self):
        no_hash = [link.split("#")[0] for link in self.all_links]
        return set(no_hash)

    def _is_link_valid(self, link):
        if not link or link == "/":
            return False
        if link.startswith(("mailto:", "tel:")):
            return False
        if not url_utils.has_valid_scheme(link, ["", "http", "https"]):
            return False
        return True

    def _analyze_link(self, link):
        if self.base_href:
            link = url_utils.make_absolute_url(self.base_href, link)
        link_host = url_utils.hostname_from_url(link)
        if not link_host or link_host == self.base_url_host:
            link_type = "internal"
            link = url_utils.make_absolute_url(self.base_url, link)
            link = url_utils.relative_url(link)
        else:
            link_type = "external"

        return {
            "type": link_type,
            "link": link
        }
