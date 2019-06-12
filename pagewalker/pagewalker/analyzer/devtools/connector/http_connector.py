import requests
from requests.exceptions import ConnectionError
import json
import time
from collections import namedtuple
from pagewalker.utilities import error_utils
from pagewalker.config import config


class HttpConnector(object):
    def __init__(self):
        self._host = "http://localhost:%s" % config.chrome_debugging_port

    @property
    def browser_socket_url(self):
        r = self._request_endpoint("/json/version")
        parsed = json.loads(r.text)
        return parsed["webSocketDebuggerUrl"]

    @property
    def browser_data(self):
        try:
            r = requests.get(self._host + "/json/version")
            return json.loads(r.text)
        except ConnectionError:
            return False

    def open_new_tab(self):
        endpoint = "/json/new"
        r = self._request_endpoint(endpoint)
        parsed = json.loads(r.text)
        socket_url_key = "webSocketDebuggerUrl"
        if socket_url_key not in parsed:
            error_utils.exit_with_message("Page socket '%s' not found in %s" % (socket_url_key, endpoint))
        NewTabData = namedtuple("NewTabData", "socket_url target_id")
        return NewTabData(parsed[socket_url_key], parsed["id"])

    def close_tab(self, target_id):
        endpoint = "/json/close/%s" % target_id
        self._request_endpoint(endpoint)

    def _request_endpoint(self, endpoint):
        timeout = 5
        url = self._host + endpoint
        start = time.time()
        while time.time() - start < timeout:
            try:
                return requests.get(url)
            except ConnectionError:
                time.sleep(1)
        msg = "Unable to connect to Chrome remote debugger URL: %s" % url
        error_utils.exit_with_message(msg)
