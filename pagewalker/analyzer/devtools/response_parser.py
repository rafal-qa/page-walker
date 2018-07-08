from pagewalker.utilities import url_utils, text_utils


class DevtoolsResponseParser(object):
    def __init__(self):
        self.general = {
            "time_start": None,
            "time_load": None,
            "time_dom_content": None,
            "main_request_id": None
        }
        self.runtime_exceptions = []
        self.network_requests = {}
        self.other_logs = []
        self.redirect_count = 0

    def get_logs(self):
        return {
            "general": self.general,
            "runtime_exceptions": self.runtime_exceptions,
            "network_requests": self.network_requests,
            "other_logs": self.other_logs
        }

    def append_response(self, messages):
        for message in messages:
            self._parse_response(message)

    def _parse_response(self, message):
        if "method" not in message:
            print("[WARN] Invalid message, no 'method' found")
            return
        if "params" not in message:
            print("[WARN] Invalid message, no 'params' found")
            return
        method = message["method"]
        params = message["params"]
        if method == "Runtime.exceptionThrown":
            self._runtime_exception_thrown(params)
        elif method == "Network.requestWillBeSent":
            self._network_request_will_be_sent(params)
        elif method == "Network.responseReceived":
            self._network_response_received(params)
        elif method == "Network.loadingFinished":
            self._network_loading_finished(params)
        elif method == "Network.requestServedFromCache":
            self._network_request_served_from_cache(params)
        elif method == "Network.loadingFailed":
            self._network_loading_failed(params)
        elif method == "Page.domContentEventFired":
            self._page_dom_content_event_fired(params)
        elif method == "Page.loadEventFired":
            self._page_load_event_fired(params)
        elif method == "Log.entryAdded":
            self._log_entry_added(params)

    def _runtime_exception_thrown(self, params):
        details = params["exceptionDetails"]
        if "exception" in details and "description" in details["exception"]:
            description = details["exception"]["description"]
        else:
            description = details["text"]
        description = text_utils.remove_whitespace(description)
        self.runtime_exceptions.append(description)

    def _network_request_will_be_sent(self, params):
        if "redirectResponse" in params:
            self._redirect_response_received(params)

        request_id = params["requestId"]
        request_time = params["timestamp"]
        url_orig = params["request"]["url"]
        url = url_utils.trim_url(url_orig)
        if not url:
            return

        new_request = {
            "time_start": request_time,
            "url": url,
            "url_is_truncated": 0 if url == url_orig else 1,
            "from_cache": None,
            "http_status": None,
            "error_name": None,
            "time_end": None,
            "data_received": None
        }

        # if this is first request:
        # - mark as main resource
        # - save request ID
        # (!) main_resource and main_request is not the same thing
        if not self.network_requests:
            new_request["is_main_resource"] = True
            self.general["time_start"] = request_time
            self.general["main_request_id"] = request_id

        self.network_requests[request_id] = new_request

    # how to handle redirects (301, 302, etc.):
    # redirect detection: "requestWillBeSent" have "redirectResponse" parameter
    # (1) close current requestId with redirect http status
    # (2) change requestId of closed request, because DevTools will use the same requestId after redirect
    # (3) current "requestWillBeSent" will be a new request to new resource
    # (4) don't change "main_request_id", because we use this only to get HTML code of final location
    # "redirectResponse" from "requestWillBeSent" is the same as "response" from "responseReceived"
    def _redirect_response_received(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return

        response = params["redirectResponse"]
        self.network_requests[request_id]["from_cache"] = response["fromDiskCache"]
        self.network_requests[request_id]["http_status"] = response["status"]
        self.network_requests[request_id]["time_end"] = params["timestamp"]
        self.network_requests[request_id]["data_received"] = response["encodedDataLength"]

        # close this request and new main request will be created with old ID
        # handle multiple redirects
        self.redirect_count += 1
        changed_request_id = "%s.r%s" % (request_id, self.redirect_count)
        self.network_requests[changed_request_id] = self.network_requests[request_id]
        del self.network_requests[request_id]

    def _network_response_received(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return

        response = params["response"]
        self._update_time_end_if_later(request_id, params["timestamp"])
        self._update_data_received(request_id, response["encodedDataLength"])
        self._set_cache_status_if_not_set(request_id, response["fromDiskCache"])
        self.network_requests[request_id]["http_status"] = response["status"]

    # responseReceived and loadingFinished can arrive in different order, we need the latest time, biggest size
    # loadingFinished is used only to provide more accurate data
    def _network_loading_finished(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        self._update_time_end_if_later(request_id, params["timestamp"])
        self._update_data_received(request_id, params["encodedDataLength"])

    # this is not the same cache type as Response[fromDiskCache]
    def _network_request_served_from_cache(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        self.network_requests[request_id]["from_cache"] = True

    def _network_loading_failed(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        self._update_time_end_if_later(request_id, params["timestamp"])
        self._set_cache_status_if_not_set(request_id, False)
        self._set_http_status_if_not_set(request_id)
        if not self.network_requests[request_id]["data_received"]:
            self.network_requests[request_id]["data_received"] = 0
        if "blockedReason" in params:
            self.network_requests[request_id]["error_name"] = "blocked:%s" % params["blockedReason"]
        else:
            self.network_requests[request_id]["error_name"] = params["errorText"]

    def _page_dom_content_event_fired(self, params):
        if not self.general["time_dom_content"]:
            self.general["time_dom_content"] = params["timestamp"]

    def _page_load_event_fired(self, params):
        if not self.general["time_load"]:
            self.general["time_load"] = params["timestamp"]

    def _log_entry_added(self, params):
        log_levels = {
            "verbose": 1,
            "info": 2,
            "warning": 3,
            "error": 4
        }
        log_sources = {
            "xml": 1,
            "javascript": 2,
            "network": 3,
            "storage": 4,
            "appcache": 5,
            "rendering": 6,
            "security": 7,
            "deprecation": 8,
            "worker": 9,
            "violation": 10,
            "intervention": 11,
            "recommendation": 12,
            "other": 13
        }
        entry = params["entry"]
        level = entry["level"]
        source = entry["source"]
        text = entry["text"]
        log = {
            "level_id": log_levels[level] if level in log_levels else 0,
            "source_id": log_sources[source] if source in log_sources else 0,
            "text": text_utils.remove_whitespace(text)
        }
        self.other_logs.append(log)

    def _update_time_end_if_later(self, request_id, timestamp):
        old_val = self.network_requests[request_id]["time_end"]
        if not old_val or timestamp > old_val:
            self.network_requests[request_id]["time_end"] = timestamp

    def _update_data_received(self, request_id, data_received):
        old_val = self.network_requests[request_id]["data_received"]
        if not old_val or data_received > old_val:
            self.network_requests[request_id]["data_received"] = data_received

    # don't overwrite requestServedFromCache event
    def _set_cache_status_if_not_set(self, request_id, cache_status):
        if not self.network_requests[request_id]["from_cache"]:
            self.network_requests[request_id]["from_cache"] = cache_status

    def _set_http_status_if_not_set(self, request_id):
        if self.network_requests[request_id]["http_status"] is None:
            self.network_requests[request_id]["http_status"] = 0
