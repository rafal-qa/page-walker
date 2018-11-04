from pagewalker.utilities import url_utils


class LinksParser(object):
    def __init__(self, base_url, base_href_tag=None):
        self.base_url = base_url
        self.base_href_tag = base_href_tag

    def filter_internal_relative(self, all_links):
        return self._filter_links_by_type(all_links, "internal")

    def filter_external(self, all_links):
        return self._filter_links_by_type(all_links, "external")

    def _filter_links_by_type(self, all_links, link_type):
        links = []
        for link in self._valid_links(all_links):
            result_type, result_link = self._analyze(link)
            if result_type == link_type:
                links.append(result_link)
        return links

    def _valid_links(self, all_links):
        valid_links = []
        for link in self._unique_links(all_links):
            if self._is_valid(link):
                valid_links.append(link)
        return valid_links

    def _unique_links(self, all_links):
        no_hash = [link.split("#")[0] for link in all_links]
        return set(no_hash)

    def _is_valid(self, link):
        if not link or link == "/":
            return False
        if link.startswith(("mailto:", "tel:")):
            return False
        if not url_utils.has_valid_scheme(link, ["", "http", "https"]):
            return False
        return True

    def _analyze(self, link):
        link = url_utils.prepend_missing_scheme(link, self.base_url)
        if self.base_href_tag:
            link = url_utils.make_absolute_url(self.base_href_tag, link)
        link_host = url_utils.hostname_from_url(link)
        base_url_host = url_utils.hostname_from_url(self.base_url)
        if not link_host or link_host == base_url_host:
            link = url_utils.make_absolute_url(self.base_url, link)
            link = url_utils.relative_url(link)
            return "internal", link
        else:
            return "external", link
