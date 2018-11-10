import requests
import urllib3
from requests.exceptions import RequestException
from pagewalker.utilities import error_utils, text_utils
from pagewalker.config import config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPHeadersAnalyzer(object):
    def __init__(self, timeout):
        self.timeout = timeout
        self.r = None

    def analyze_for_chrome(self, url, cookies_data):
        cookie_jar = self._prepare_cookie_jar(cookies_data) if cookies_data else None
        request_success, exception_type = self._http_get_only_headers(url, False, cookie_jar)
        if not request_success:
            return {
                "status": "request_exception",
                "http_code": None,
                "error_name": exception_type
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

    def check_valid_for_analysis(self, url):
        cookie_jar = self._prepare_cookie_jar(config.custom_cookies_data) if config.custom_cookies_data else None
        request_success, exception_type = self._http_get_only_headers(url, False, cookie_jar)
        if not request_success:
            error_utils.exit_with_message("Start URL %s" % exception_type)
        if self.r.is_redirect:
            msg = "Start URL %s redirects to %s" % (url, self.r.headers["Location"])
            msg += "\nPlease provide non-redirecting URL"
            error_utils.exit_with_message(msg)
        if not self.r.ok:
            error_utils.exit_with_message("Start URL returned HTTP error '%s'" % self._http_status())
        if not self._is_http():
            error_utils.exit_with_message("Start URL is not HTML page")

    def analyze_for_external_links_check(self, url):
        request_success, exception_name = self._http_get_only_headers(url, True, None)
        if not request_success:
            return {
                "redirect_url": None,
                "http_code": None,
                "error_name": exception_name
            }
        return {
            "redirect_url": self._redirect_url(),
            "http_code": self.r.status_code,
            "error_name": None
        }

    def _prepare_cookie_jar(self, cookies_data):
        jar = requests.cookies.RequestsCookieJar()
        for single_cookie_data in cookies_data:
            optional_args = self._cookie_jar_optional_args(single_cookie_data)
            jar.set(single_cookie_data["name"], single_cookie_data["value"], **optional_args)
        return jar

    def _cookie_jar_optional_args(self, single_cookie_data):
        optional_args = {}
        for option in ["domain", "path"]:
            if option in single_cookie_data:
                optional_args[option] = single_cookie_data[option]
        return optional_args

    def _http_get_only_headers(self, url, allow_redirects, cookie_jar):
        headers = {"user-agent": config.user_agent}
        if config.http_basic_auth_data:
            headers["authorization"] = "Basic %s" % text_utils.base64_encode(config.http_basic_auth_data)
        hooks = {"response": lambda response, *args, **kwargs: response.close()}
        try:
            self.r = requests.get(url, headers=headers, hooks=hooks, timeout=self.timeout,
                                  allow_redirects=allow_redirects, cookies=cookie_jar, verify=False)
            return True, None
        except RequestException as e:
            return False, type(e).__name__

    def _content_type(self):
        return self.r.headers["Content-Type"] if "Content-Type" in self.r.headers else None

    def _content_length(self):
        return int(self.r.headers["Content-Length"]) if "Content-Length" in self.r.headers else None

    def _http_status(self):
        return self.r.headers["Status"] if "Status" in self.r.headers else self.r.status_code

    def _is_http(self):
        return "Content-Type" in self.r.headers and self.r.headers["Content-Type"].startswith("text/html")

    def _redirect_url(self):
        return self.r.url if self.r.history else None
