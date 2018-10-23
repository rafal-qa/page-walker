import requests
import urllib3
from requests.exceptions import RequestException
from pagewalker.utilities import error_utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPHeadersAnalyzer(object):
    def __init__(self, timeout):
        self.timeout = timeout
        self.r = None

    def analyze_for_chrome(self, url):
        request_result = self._head_request(url)
        if request_result is not True:
            return {
                "status": "request_exception",
                "http_code": None,
                "error_name": request_result
            }
        if self.r.is_redirect:
            return {
                "status": "is_redirect",
                "http_code": self.r.status_code,
                "location": self.r.headers["Location"] if "Location" in self.r.headers else None
            }
        if not self.r.ok:
            return {
                "status": "is_error_code",
                "http_code": self.r.status_code
            }
        if not self._is_http():
            return {
                "status": "is_file",
                "http_code": self.r.status_code,
                "content_type": self._content_type(),
                "content_length": self._content_length()
            }
        return {
            "status": "ok",
            "http_code": self.r.status_code
        }

    def check_200_ok_html(self, url):
        request_result = self._head_request(url)
        if request_result is not True:
            error_utils.exit_with_message("Start URL %s" % request_result)
        if self.r.is_redirect:
            msg = "Start URL %s redirects to %s" % (url, self.r.headers["Location"])
            msg += "\nPlease provide non-redirecting URL"
            error_utils.exit_with_message(msg)
        if not self.r.ok:
            error_utils.exit_with_message("Start URL returned HTTP error '%s'" % self._http_status())
        if not self._is_http():
            error_utils.exit_with_message("Start URL is not HTML page")

    def _head_request(self, url):
        headers = {"user-agent": "Mozilla/5.0 AppleWebKit/537.36 Chrome/66.0.3359.181"}
        try:
            self.r = requests.head(url, headers=headers, timeout=self.timeout, allow_redirects=False, verify=False)
            return True
        except RequestException as e:
            return type(e).__name__

    def _content_type(self):
        return self.r.headers["Content-Type"] if "Content-Type" in self.r.headers else None

    def _content_length(self):
        return int(self.r.headers["Content-Length"]) if "Content-Length" in self.r.headers else None

    def _http_status(self):
        return self.r.headers["Status"] if "Status" in self.r.headers else self.r.status_code

    def _is_http(self):
        return "Content-Type" in self.r.headers and self.r.headers["Content-Type"].startswith("text/html")
