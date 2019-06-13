from abc import ABCMeta, abstractmethod
from pagewalker.utilities import text_utils
from pagewalker.config import config


class BrowserAbstract(metaclass=ABCMeta):
    def __init__(self, devtools_protocol):
        self._devtools_protocol = devtools_protocol

    def connect(self):
        self._start_browser()
        self._print_start_message()
        self._open_new_tab()

    def configure(self):
        self._enable_features()
        self._enable_mobile_emulation()
        self._clear_browser_data()
        self._set_custom_cookies()
        self._set_http_auth_header()

    @abstractmethod
    def _start_browser(self):
        pass

    @abstractmethod
    def _print_start_message(self):
        pass

    def _open_new_tab(self):
        self._devtools_protocol.open_tab()

    def _enable_features(self):
        self._devtools_protocol.send_command("Network.enable")
        self._devtools_protocol.send_command("Log.enable")
        self._devtools_protocol.send_command("Page.enable")
        self._devtools_protocol.send_command("Page.setDownloadBehavior", {"behavior": "deny"})  # EXPERIMENTAL
        self._devtools_protocol.send_command("DOM.enable")
        self._devtools_protocol.send_command("Runtime.enable")

    def _enable_mobile_emulation(self):
        pass

    def _clear_browser_data(self):
        pass

    def _set_custom_cookies(self):
        if config.custom_cookies_data:
            for single_cookie_data in config.custom_cookies_data:
                self._set_cookie(single_cookie_data)

    def _set_cookie(self, cookie_data):
        # "At least one of the url and domain needs to be specified"
        if "domain" not in cookie_data:
            cookie_data["url"] = config.start_url
        # .ini file is case-insensitive, but DevTools protocol requires "httpOnly"
        if "httponly" in cookie_data:
            cookie_data["httpOnly"] = cookie_data.pop("httponly")
        self._devtools_protocol.send_command("Network.setCookie", cookie_data)

    def _set_http_auth_header(self):
        if config.http_basic_auth_data:
            headers = {"authorization": "Basic %s" % text_utils.base64_encode(config.http_basic_auth_data)}
            self._devtools_protocol.send_command("Network.setExtraHTTPHeaders", {"headers": headers})

    @property
    @abstractmethod
    def browser_type(self):
        pass

    @property
    @abstractmethod
    def window_size(self):
        pass

    @property
    def user_agent(self):
        version_data = self._devtools_protocol.send_command("Browser.getVersion")
        return version_data["userAgent"]

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def close_previously_unclosed(self):
        pass
