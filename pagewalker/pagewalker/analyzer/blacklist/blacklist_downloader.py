from os import path
import json
import re
from . import blacklist_downloader_file
from pagewalker.utilities import error_utils
from pagewalker.config import config


class BlacklistDownloader(object):
    def __init__(self):
        self.domains = []
        self.file = blacklist_downloader_file.BlacklistDownloaderFile()

    def update(self):
        if not config.domain_blacklist_auto_update:
            self._disable_if_no_file()
            return
        domain_lists = self._get_domain_lists()
        if not domain_lists:
            self._update_failed()
            return
        for list_name, url_list in domain_lists.items():
            self._add_domains_from_list(list_name, url_list)
        self._save_unique_domains_to_file()

    def _get_domain_lists(self):
        list_name = "domain_lists"
        self.file.update_cache(config.domain_blacklist_url, list_name)
        domain_lists = self.file.get_from_cache(list_name)
        try:
            domain_lists_json = json.loads(domain_lists)
        except ValueError:
            file_name = self.file.file_names(list_name)[0]
            print("[FAIL] Unable to decode JSON file: %s" % file_name)
            return False
        if not domain_lists_json:
            return False
        domain_lists_data = {}
        for list_name, url_list in domain_lists_json.items():
            domain_lists_data[list_name] = url_list
        return domain_lists_data

    def _add_domains_from_list(self, list_name, url_list):
        content = self._get_content_from_first_url(list_name, url_list)
        if not content:
            return
        domains = content.split("\n")
        domains = [x.strip() for x in domains]
        for domain in domains:
            self._add_domain(domain)

    def _get_content_from_first_url(self, list_name, url_list):
        for url in url_list:
            if self.file.update_cache(url, list_name):
                break
        return self.file.get_from_cache(list_name)

    def _add_domain(self, domain):
        domain = domain.lower()
        if domain.startswith("www."):
            domain = domain.replace("www.", "")
        plain_domain = re.match(r"^[a-z0-9.\-]+$", domain)
        if plain_domain:
            self.domains.append(domain)
            return
        adblock_format = re.match(r"^\|\|([a-z0-9.\-]+)\^$", domain)
        if adblock_format:
            domain = adblock_format.group(1)
            self.domains.append(domain)

    def _save_unique_domains_to_file(self):
        domains = set(self.domains)
        with open(config.domain_blacklist_file, 'w') as f:
            f.write("\n".join(domains))
        print("[INFO] %s domains saved to local blacklist" % len(domains))

    def _disable_if_no_file(self):
        if not path.isfile(config.domain_blacklist_file):
            config.domain_blacklist_enabled = False
            msg = "Blacklist file not found, but auto update is disabled"
            msg += "\nDomain blacklist checking was disabled"
            error_utils.show_warning(msg)

    def _update_failed(self):
        msg = "Failed to update domains list"
        if path.isfile(config.domain_blacklist_file):
            msg += "\nThe previously saved blacklist will be used"
        else:
            config.domain_blacklist_enabled = False
            msg += "\nDomain blacklist checking was disabled"
        error_utils.show_warning(msg)
