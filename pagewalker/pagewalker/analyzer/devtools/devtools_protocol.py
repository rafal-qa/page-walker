from .connector import websocket_connector, http_connector


class DevtoolsProtocol(object):
    def __init__(self):
        self._http = http_connector.HttpConnector()
        self.tab_socket = None
        self.tab_target_id = None

    @property
    def browser_data(self):
        return self._http.browser_data

    def open_tab(self):
        new_tab = self._http.open_new_tab()
        self.tab_socket = websocket_connector.WebsocketConnector(new_tab.socket_url)
        self.tab_target_id = new_tab.target_id

    def close_tab(self):
        self._assert_tab_exists()
        self.tab_socket.close_connection()
        self._http.close_tab(self.tab_target_id)
        self._delete_tab_data()

    def _delete_tab_data(self):
        self.tab_socket = None
        self.tab_target_id = None

    def send_command(self, method, params=None):
        self._assert_tab_exists()
        if not params:
            params = {}
        return self.tab_socket.send(method, params)

    def send_command_return(self, method, params):
        self._assert_tab_exists()
        return self.tab_socket.send_return(method, params)

    def read_until_events(self, events):
        self._assert_tab_exists()
        return self.tab_socket.read_until_events(events)

    def read_until_timeout(self, timeout):
        self._assert_tab_exists()
        return self.tab_socket.read_until_timeout(timeout)

    def _assert_tab_exists(self):
        if not self.tab_socket or not self.tab_target_id:
            raise RuntimeError("Operation not supported, browser tab does not exists")

    def get_cookies_for_url(self, url):
        cookies_data = []
        result = self.send_command("Network.getCookies", {"urls": [url]})
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

    def send_browser_close(self):
        socket_url = self._http.browser_socket_url
        browser_socket = websocket_connector.WebsocketConnector(socket_url)
        browser_socket.send("Browser.close", {})
        browser_socket.close_connection()
