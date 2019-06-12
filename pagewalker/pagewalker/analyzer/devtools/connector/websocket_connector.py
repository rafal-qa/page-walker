import json
import time
import websocket
from websocket import WebSocketTimeoutException, WebSocketConnectionClosedException
from pagewalker.utilities import error_utils
from pagewalker.config import config


class WebsocketConnector(object):
    def __init__(self, socket_url):
        self._socket = websocket.create_connection(socket_url)
        self._send_id = 0

    def close_connection(self):
        self._socket.send_close()

    def send_return(self, method, params):
        self._send_id += 1
        send_data = {
            "id": self._send_id,
            "method": method,
            "params": params
        }
        self._socket.send(json.dumps(send_data))
        confirm, messages = self._read_until_confirm(method)
        if confirm and "result" in confirm:
            result = confirm["result"]
        else:
            result = False
        return result, messages

    def send(self, method, params):
        self._send_id += 1
        send_data = {
            "id": self._send_id,
            "method": method,
            "params": params
        }
        self._socket.send(json.dumps(send_data))
        confirm, _ = self._read_until_confirm(method)
        if confirm and "result" in confirm:
            return confirm["result"]
        else:
            return False

    def _read_until_confirm(self, method):
        self._socket.settimeout(config.chrome_timeout)
        confirm_message = None
        previous_messages = []
        start = time.time()
        while time.time() - start < config.chrome_timeout:
            try:
                message = self._socket.recv()
            except WebSocketTimeoutException:
                break
            except WebSocketConnectionClosedException:
                self._lost_connection_error()
                break
            parsed = json.loads(message)
            if "id" in parsed and parsed["id"] == self._send_id:
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
        self._socket.settimeout(config.chrome_timeout)
        found = False
        messages = []
        start = time.time()
        while time.time() - start < config.chrome_timeout:
            try:
                message = self._socket.recv()
            except WebSocketTimeoutException:
                break
            except WebSocketConnectionClosedException:
                self._lost_connection_error()
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
        self._socket.settimeout(timeout)
        all_messages = []  # all messages received from socket
        start = time.time()
        while time.time() - start < timeout:
            try:
                message = self._socket.recv()
            except WebSocketTimeoutException:
                break
            except WebSocketConnectionClosedException:
                self._lost_connection_error()
                break
            parsed = json.loads(message)
            all_messages.append(parsed)
        return all_messages

    def _lost_connection_error(self):
        error_utils.exit_with_message("Lost connection to Chrome remote debugger")
