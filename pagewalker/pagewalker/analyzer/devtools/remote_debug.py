from . import devtools_protocol, remote_debug_actions
from pagewalker.analyzer import initial_actions
from .browser import browser_factory
from pagewalker.utilities import error_utils
from pagewalker.config import config


class RemoteDebug(object):
    def __init__(self):
        self._devtools_protocol = devtools_protocol.DevtoolsProtocol()
        browser_class = browser_factory.get_new_browser()
        self._browser = browser_class(self._devtools_protocol)

    def start_session(self):
        self._close_existing_session()
        self._browser.connect()
        self._browser.configure()
        self._apply_initial_actions()
        self._update_requests_user_agent()

    def _close_existing_session(self):
        browser_data = self._devtools_protocol.browser_data
        if browser_data:
            browser_class = browser_factory.get_running_browser(browser_data)
            browser = browser_class(self._devtools_protocol)
            browser.close_previously_unclosed()

    def _apply_initial_actions(self):
        if config.initial_actions_data:
            initial_actions.InitialActions(self, self._devtools_protocol)

    def _update_requests_user_agent(self):
        config.requests_user_agent = self._browser.user_agent

    def end_session(self):
        if config.chrome_close_on_finish:
            self._devtools_protocol.close_tab()
            self._browser.close()
        else:
            self._show_keep_open_warning()

    def _show_keep_open_warning(self):
        msg = "Keeping browser and remote debugger open"
        msg += "\nYou can manually inspect it on http://localhost:%s" % config.chrome_debugging_port
        error_utils.show_warning(msg)

    def scroll_to_bottom(self):
        actions = remote_debug_actions.RemoteDebugActions(self._devtools_protocol)
        actions.scroll_to_bottom()

    def get_cookies(self, url):
        return self._devtools_protocol.get_cookies_for_url(url)

    def open_url(self, url):
        page_result, messages_before = self._devtools_protocol.send_command_return("Page.navigate", {"url": url})
        if not page_result:
            return False

        events_for_wait = [
            "Page.loadEventFired",
            "Page.domContentEventFired"
        ]
        events_found, messages_after = self._devtools_protocol.read_until_events(events_for_wait)
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
        result = self._devtools_protocol.send_command("Network.getResponseBody", {"requestId": request_id})
        if not result:
            return ""
        return result["body"] if "body" in result else ""

    def get_html_dom(self):
        result = self._devtools_protocol.send_command("DOM.getDocument")
        if not result:
            return ""
        root_node = result["root"]["nodeId"]
        html_object = self._devtools_protocol.send_command("DOM.getOuterHTML", {"nodeId": root_node})
        return html_object["outerHTML"] if html_object else ""

    def wait(self, wait_time):
        return self._devtools_protocol.read_until_timeout(wait_time)

    def get_version(self):
        return self._devtools_protocol.send_command("Browser.getVersion")
