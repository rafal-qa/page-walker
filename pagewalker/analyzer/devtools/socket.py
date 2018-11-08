import time
import requests
from requests.exceptions import ConnectionError
import json
import websocket
from websocket import WebSocketTimeoutException, WebSocketConnectionClosedException
from pagewalker.utilities import error_utils
from pagewalker.config import config


class DevtoolsSocket(object):
    def __init__(self):
        self.page_socket = None
        self.send_id = 0

    # find *page* debugger socket URL
    # can be several URLs, we want one with "page" type (not "background_page", etc.)
    def connect_to_remote_debugger(self):
        url = "http://localhost:%s/json" % config.chrome_debugging_port
        r = self._try_to_connect_until_timeout(url)
        parsed = json.loads(r.text)
        page_debugger_url = False
        for item in parsed:
            if item["type"] == "page":
                page_debugger_url = item["webSocketDebuggerUrl"]
                break
        if not page_debugger_url:
            error_utils.exit_with_message("Page socket debugger URL not found in %s" % url)

        self.page_socket = websocket.create_connection(page_debugger_url)

    def _try_to_connect_until_timeout(self, url):
        max_retries = 10
        for i in range(0, max_retries):
            time.sleep(1)
            try:
                return requests.get(url)
            except ConnectionError:
                pass
        error_utils.exit_with_message(
            "Unable to connect to Chrome remote debugger on %s (see log file for details)" % url
        )

    def close_existing_session(self):
        url = "http://localhost:%s/json" % config.chrome_debugging_port
        try:
            requests.get(url)
        except ConnectionError:
            return
        msg = "Chrome remote debugger already running on port %s." % config.chrome_debugging_port
        msg += "\nClosing it now. Use different ports to run multiple instances."
        error_utils.show_warning(msg)
        self.send_browser_close()
        time.sleep(5)

    def close_page_connection(self):
        self.page_socket.send_close()

    # find *browser* debugger socket URL
    def send_browser_close(self):
        r = requests.get("http://localhost:%s/json/version" % config.chrome_debugging_port)
        parsed = json.loads(r.text)
        browser_debugger_url = parsed["webSocketDebuggerUrl"]
        browser_socket = websocket.create_connection(browser_debugger_url)
        self.send("Browser.close", None, browser_socket)
        browser_socket.send_close()

    # 1. send a message to page_socket
    # 2. save all previous unread messages
    # 3. wait for confirmation of receiving the message
    def send_return(self, method, params):
        self.send_id += 1
        send_data = {
            "id": self.send_id,
            "method": method,
            "params": params
        }
        self.page_socket.send(json.dumps(send_data))
        confirm, messages = self._read_until_confirm(self.send_id, method, self.page_socket)
        if confirm and "result" in confirm:
            result = confirm["result"]
        else:
            result = False
        return result, messages

    # 1. send a message to any socket (default: page_socket)
    # 2. discard all previous unread messages
    # 3. wait for confirmation of receiving the message
    def send(self, method, params=None, socket=None):
        if not socket:
            socket = self.page_socket
        self.send_id += 1
        if not params:
            params = {}
        send_data = {
            "id": self.send_id,
            "method": method,
            "params": params
        }
        socket.send(json.dumps(send_data))
        confirm, _ = self._read_until_confirm(self.send_id, method, socket)
        if confirm and "result" in confirm:
            return confirm["result"]
        else:
            return False

    def _read_until_confirm(self, send_id, method, socket):
        socket.settimeout(config.chrome_timeout)
        confirm_message = None
        previous_messages = []
        start = time.time()
        while time.time() - start < config.chrome_timeout:
            try:
                message = socket.recv()
            except WebSocketTimeoutException:
                break
            except WebSocketConnectionClosedException:
                error_utils.socket_lost_connection()
                break
            parsed = json.loads(message)
            if "id" in parsed and parsed["id"] == send_id:
                if "error" in parsed:
                    print("[FAIL] %s | %s" % (method, parsed["error"]["message"]))
                else:
                    confirm_message = parsed
                break
            else:
                previous_messages.append(parsed)
        return confirm_message, previous_messages

    # return:
    #   all messages until all of desired events was found
    #   events_found - False if some of events was not found in timeout
    def read_until_events(self, events):
        self.page_socket.settimeout(config.chrome_timeout)
        found = False
        messages = []
        start = time.time()
        while time.time() - start < config.chrome_timeout:
            try:
                message = self.page_socket.recv()
            except WebSocketTimeoutException:
                break
            except WebSocketConnectionClosedException:
                error_utils.socket_lost_connection()
                break
            parsed = json.loads(message)
            messages.append(parsed)
            if "method" in parsed and parsed["method"] in events:
                events.remove(parsed["method"])
                if not events:
                    found = True
                    break
        return found, messages

    # read the rest of messages
    # wait for any new messages until timeout
    def read_until_timeout(self, timeout):
        self.page_socket.settimeout(timeout)
        all_messages = []  # all messages received from socket
        start = time.time()
        while time.time() - start < timeout:
            try:
                message = self.page_socket.recv()
            except WebSocketTimeoutException:
                break
            except WebSocketConnectionClosedException:
                error_utils.socket_lost_connection()
                break
            parsed = json.loads(message)
            all_messages.append(parsed)
        return all_messages
