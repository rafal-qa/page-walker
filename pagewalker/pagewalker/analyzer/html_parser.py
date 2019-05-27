try:
    from html.parser import HTMLParser  # Python 3
except ImportError:
    from HTMLParser import HTMLParser  # Python 2


class MyHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.base_href = None
        self.all_links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._handle_a(attrs)
        if tag == "base":
            self._handle_base(attrs)

    def _handle_a(self, attrs):
        link = dict(attrs).get("href")
        if link:
            self.all_links.append(link.strip())

    def _handle_base(self, attrs):
        if self.base_href:
            return
        link = dict(attrs).get("href")
        if link:
            self.base_href = link.strip()

    def get_found_links(self):
        return self.all_links

    def get_base_href(self):
        return self.base_href
