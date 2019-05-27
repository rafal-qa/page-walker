import time
from os import path
import requests
from requests.exceptions import RequestException
from pagewalker.utilities import filesystem_utils
from pagewalker.config import config


class BlacklistDownloaderFile(object):
    def __init__(self):
        self.cache_dir = path.join(config.domain_blacklist_dir, "cache")
        filesystem_utils.make_dir_if_not_exists(self.cache_dir)

    def get_from_cache(self, list_name):
        file_content = self.file_names(list_name)[0]
        if not path.isfile(file_content):
            return False
        return self._read_content(file_content)

    def update_cache(self, url, list_name):
        if self._is_cache_valid(list_name):
            return True
        data = self._download_file(url)
        if len(data) > 0:
            self._save_to_cache(list_name, data)
            return True
        return False

    def _is_cache_valid(self, list_name):
        file_content, file_updated = self.file_names(list_name)
        if not path.isfile(file_content) or not path.isfile(file_updated):
            return False
        with open(file_updated, "r") as f:
            updated = f.read()
        return not self._cache_expired(updated)

    def _read_content(self, file_name):
        with open(file_name, "r") as f:
            return f.read()

    def _save_to_cache(self, list_name, data):
        file_content, file_updated = self.file_names(list_name)
        with open(file_content, "w") as f:
            f.write(data)
        with open(file_updated, "w") as f:
            timestamp = str(int(time.time()))
            f.write(timestamp)

    def _download_file(self, url):
        headers = {"user-agent": config.user_agent}
        try:
            r = requests.get(url, headers=headers, timeout=30)
        except RequestException as e:
            print("[FAIL] Unable to download file %s (%s)" % (url, type(e).__name__))
            return ""
        if not r.ok:
            print("[FAIL] Unable to download file %s (HTTP status: %s)" % (url, r.status_code))
            return ""
        print("[ OK ] Downloaded file %s" % url)
        return r.text

    def file_names(self, file_name):
        file_content = path.join(self.cache_dir, "%s.txt" % file_name)
        file_updated = path.join(self.cache_dir, "%s_updated.txt" % file_name)
        return file_content, file_updated

    def _cache_expired(self, updated):
        cache_expiry_seconds = config.domain_blacklist_cache_expiry * 3600
        return time.time() - int(updated) > cache_expiry_seconds
