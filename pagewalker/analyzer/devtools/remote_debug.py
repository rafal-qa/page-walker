from os import path
from subprocess import Popen
from . import socket
from pagewalker.utilities import filesystem_utils, error_utils


class DevtoolsRemoteDebug(object):
    def __init__(self, headless, close_on_finish, debugging_port, profile_dir, chrome_timeout, window_size,
                 chrome_binary, ignore_cert, current_data_dir):
        self.headless = headless
        self.close_on_finish = close_on_finish
        self.profile_dir = profile_dir
        self.log_file = path.join(current_data_dir, "chrome_run.log")
        self.chrome = chrome_binary
        self.debugger_socket = socket.DevtoolsSocket(debugging_port, chrome_timeout)

        command_parts = [
            self.chrome,
            "--remote-debugging-port=%s" % debugging_port,
            "--window-size=%s" % window_size.replace("x", ","),
            "--no-first-run",
            "--user-data-dir=%s" % profile_dir
        ]
        if headless:
            command_parts.append("--headless")
            command_parts.append("--disable-gpu")
        if ignore_cert:
            command_parts.append("--ignore-certificate-errors")

        self.command_parts = command_parts

    def start_session(self):
        self.debugger_socket.close_existing_session()
        filesystem_utils.clean_directory(self.profile_dir)
        chrome_log = open(self.log_file, "w")
        try:
            Popen(self.command_parts, stdout=chrome_log, stderr=chrome_log)
        except OSError:
            message = "Chrome not found at location: %s" % self.chrome
            message += "\nFind location of Chrome/Chromium in your system and configure it in:"
            message += "\n* config/default.ini file (option: chrome_binary)"
            message += "\n* or command line parameter --chrome-binary"
            error_utils.exit_with_message(message)
        self._print_start_message()
        self.debugger_socket.connect_to_remote_debugger()
        self._enable_features()

    def _print_start_message(self):
        print("")
        print("Running Chrome in remote debugger mode")
        print("Saving output to log file: %s" % self.log_file)
        print("")

    def _enable_features(self):
        self.debugger_socket.send("Network.enable")
        self.debugger_socket.send("Log.enable")
        self.debugger_socket.send("Page.enable")
        self.debugger_socket.send("Page.setDownloadBehavior", {"behavior": "deny"})  # EXPERIMENTAL
        self.debugger_socket.send("DOM.enable")
        self.debugger_socket.send("Runtime.enable")

    def end_session(self):
        self.debugger_socket.close_page_connection()
        if self.headless or self.close_on_finish:
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

    def scroll_to_bottom(self):
        self.debugger_socket.send("Runtime.evaluate", {
            "expression": "window.scrollTo(0,document.body.scrollHeight);",
            "awaitPromise": True
        })

    def wait(self, wait_time):
        return self.debugger_socket.read_until_timeout(wait_time)

    def get_version(self):
        return self.debugger_socket.send("Browser.getVersion")
