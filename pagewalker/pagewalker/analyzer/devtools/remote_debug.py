from . import socket, remote_debug_actions
from pagewalker.analyzer import initial_actions
from pagewalker.analyzer.browser import chrome_desktop
from pagewalker.utilities import text_utils
from pagewalker.config import config


class RemoteDebug(object):
    def __init__(self):
        self.debugger_socket = socket.DevtoolsSocket()
        self.actions = remote_debug_actions.RemoteDebugActions(self.debugger_socket)
        self.browser = chrome_desktop.ChromeDesktop()

    def start_session(self):
        self.debugger_socket.close_existing_session()
        self.browser.run()
        self.debugger_socket.connect_to_remote_debugger()
        self._enable_features()
        self._set_custom_cookies()
        self._set_http_auth_header()
        self._initial_actions()
        self._update_user_agent()

    def _enable_features(self):
        self.debugger_socket.send("Network.enable")
        self.debugger_socket.send("Log.enable")
        self.debugger_socket.send("Page.enable")
        self.debugger_socket.send("Page.setDownloadBehavior", {"behavior": "deny"})  # EXPERIMENTAL
        self.debugger_socket.send("DOM.enable")
        self.debugger_socket.send("Runtime.enable")

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
        self.debugger_socket.send("Network.setCookie", cookie_data)

    def _set_http_auth_header(self):
        if config.http_basic_auth_data:
            headers = {"authorization": "Basic %s" % text_utils.base64_encode(config.http_basic_auth_data)}
            self.debugger_socket.send("Network.setExtraHTTPHeaders", {"headers": headers})

    def _initial_actions(self):
        if config.initial_actions_data:
            initial_actions.InitialActions(self).execute()

    def _update_user_agent(self):
        config.user_agent = self.get_version()["userAgent"]

    def get_cookies_for_url(self, url):
        cookies_data = []
        result = self.debugger_socket.send("Network.getCookies", {"urls": [url]})
        if not result or not result["cookies"]:
            return cookies_data
        for cookie in result["cookies"]:
            cookies_data.append({
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie["path"]
            })
        return cookies_data

    def end_session(self):
        self.debugger_socket.close_page_connection()
        if config.chrome_headless or config.chrome_close_on_finish:
            self.debugger_socket.send_browser_close()

    def open_url(self, url):
        page_result, messages_before = self.debugger_socket.send_return("Page.navigate", {"url": url})
        if not page_result:
            return False

        events_for_wait = [
            "Page.loadEventFired",
            "Page.domContentEventFired"
        ]
        events_found, messages_after = self.debugger_socket.read_until_events(events_for_wait)
        if not events_found:
            return False

        messages_filtered = self._discard_non_page_messages(page_result, messages_before)
        return messages_filtered + messages_after

    def _discard_non_page_messages(self, page_data, messages):
        filtered = []
        if "loaderId" not in page_data:
            return filtered
        loader_id = page_data["loaderId"]

        for msg in messages:
            if "params" in msg and "loaderId" in msg["params"] and msg["params"]["loaderId"] == loader_id:
                filtered.append(msg)

        return filtered

    def get_html_raw(self, request_id):
        result = self.debugger_socket.send("Network.getResponseBody", {"requestId": request_id})
        if not result:
            return ""
        return result["body"] if "body" in result else ""

    def get_html_dom(self):
        result = self.debugger_socket.send("DOM.getDocument")
        if not result:
            return ""
        root_node = result["root"]["nodeId"]
        html_object = self.debugger_socket.send("DOM.getOuterHTML", {"nodeId": root_node})
        return html_object["outerHTML"] if html_object else ""

    def wait(self, wait_time):
        return self.debugger_socket.read_until_timeout(wait_time)

    def get_version(self):
        return self.debugger_socket.send("Browser.getVersion")
