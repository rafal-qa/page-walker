import requests
import urllib3
from requests.exceptions import RequestException
from pagewalker.utilities import error_utils, text_utils, url_utils
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

    def check_valid_first_url(self):
        url = self._get_first_url()
        cookie_jar = self._prepare_cookie_jar(config.custom_cookies_data) if config.custom_cookies_data else None
        request_success, exception_type = self._http_get_only_headers(url, True, cookie_jar)
        if not request_success:
            error_utils.exit_with_message("Start URL error: %s" % exception_type)
        self._check_redirect_to_other_host(url)
        self._check_error_code(url)
        self._check_no_html_page(url)

    def _get_first_url(self):
        if config.initial_actions_file and config.initial_actions_url:
            return config.initial_actions_url
        else:
            return config.start_url

    def _check_redirect_to_other_host(self, url):
        redirect_url = self._redirect_url()
        if not redirect_url:
            return
        if url_utils.hostname_from_url(url) == url_utils.hostname_from_url(redirect_url):
            return
        msg = "%s redirects to other host %s" % (url, redirect_url)
        msg += "\nPlease provide non-redirecting URL"
        error_utils.exit_with_message(msg)

    def _check_error_code(self, url):
        if self.r.ok:
            return
        status_code, status_name = self._http_status()
        msg = "%s returned HTTP error: %s %s" % (url, status_code, status_name)
        if status_code == 401:
            msg += "\nHint: Use --http-auth option to provide HTTP authentication credentials"
        error_utils.exit_with_message(msg)

    def _check_no_html_page(self, url):
        if not self._is_http():
            error_utils.exit_with_message("%s is not HTML page" % url)

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
        error_codes = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            408: "Request Timeout",
            410: "Gone",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        code = self.r.status_code
        name = error_codes[code] if code in error_codes else ""
        return code, name

    def _is_http(self):
        return "Content-Type" in self.r.headers and self.r.headers["Content-Type"].startswith("text/html")

    def _redirect_url(self):
        return self.r.url if self.r.history else None
