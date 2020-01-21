import argparse
import requests
import sys


systems = ["win32", "win64", "linux64", "mac"]

parser = argparse.ArgumentParser()
parser.add_argument("--system", required=True, help="Operating system", choices=systems)
parser.add_argument("--version", help="Major Chrome version number (example: 79). If omitted, download latest.")
args = parser.parse_args()


class ChromeDownloader(object):
    def __init__(self, major_version, version_os, download_os, file_name):
        self.major_version = major_version
        self.version_os = version_os
        self.download_os = download_os
        self.file_name = file_name
        self.invalid_links = []

    def download_link(self):
        if self.major_version:
            return self._download_version()
        else:
            return self._download_latest()

    def _download_version(self):
        versions = self._exact_versions()
        for version in versions:
            position = self._base_position(version)
            link = "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/" \
                   + self.download_os + "%2F" + position + "%2F" + self.file_name + "?alt=media"
            if self._valid_link(link):
                return link
        return False

    def _download_latest(self):
        position = self._get_latest_position()
        link = "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/" \
               + self.download_os + "%2F" + position + "%2F" + self.file_name + "?alt=media"
        if self._valid_link(link):
            return link
        return False

    def _get_latest_position(self):
        url = "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/" \
               + self.download_os + "%2FLAST_CHANGE?alt=media"
        r = requests.get(url)
        return r.text

    def _exact_versions(self):
        url = "https://omahaproxy.appspot.com/history.json?os=%s" % self.version_os
        parsed = self._get_json(url)
        versions = []
        for item in parsed:
            version = item["version"]
            if self._match_main_version(version):
                versions.append(version)
        return versions

    def _base_position(self, version):
        url = "https://omahaproxy.appspot.com/deps.json?version=%s" % version
        parsed = self._get_json(url)
        return parsed["chromium_base_position"]

    def _valid_link(self, url):
        if url in self.invalid_links:
            return False
        r = requests.head(url, timeout=10)
        if r.headers["Content-Type"].startswith("application/"):
            return True
        else:
            self.invalid_links.append(url)
            return False

    def _match_main_version(self, version):
        parts = version.split(".")
        return parts[0] == self.major_version

    def _get_json(self, url):
        r = requests.get(url)
        return r.json()


systems_data = {
    "omahaproxy_os": {
        "win32": "win",
        "win64": "win64",
        "linux64": "linux",
        "mac": "mac"
    },
    "download_os": {
        "win32": "Win",
        "win64": "Win_x64",
        "linux64": "Linux_x64",
        "mac": "Mac"
    },
    "download_filename": {
        "win32": "chrome-win32.zip",
        "win64": "chrome-win32.zip",
        "linux64": "chrome-linux.zip",
        "mac": "chrome-mac.zip"
    }
}

os = args.system
downloader = ChromeDownloader(
    args.version,
    systems_data["omahaproxy_os"][os],
    systems_data["download_os"][os],
    systems_data["download_filename"][os]
)
link = downloader.download_link()
if link:
    print(link)
else:
    print("ERROR: Link not found")
    sys.exit(1)
