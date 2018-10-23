from pagewalker.utilities import text_utils


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
        self.console_logs = []
        self.main_request_http_status = None

    def get_logs(self):
        return {
            "general": self.general,
            "runtime_exceptions": self.runtime_exceptions,
            "network_requests": self.network_requests.values(),
            "console_logs": self.console_logs
        }

    def get_main_request_http_status(self):
        return self.main_request_http_status

    def append_response(self, messages):
        for message in messages:
            if self._valid_response(message):
                self._parse_response(message)

    def _valid_response(self, message):
        required_keys = ["method", "params"]
        for key in required_keys:
            if key not in message:
                print("[WARN] Invalid message, no '%s' found" % key)
                return False
        return True

    def _parse_response(self, message):
        method_name = text_utils.camelcase_to_underscore(message["method"]).replace(".", "_")
        if hasattr(self, method_name):
            instance_method = getattr(self, method_name)
            instance_method(message["params"])

    def runtime_exception_thrown(self, params):
        details = params["exceptionDetails"]
        if "exception" in details and "description" in details["exception"]:
            description = details["exception"]["description"]
        else:
            description = details["text"]
        description = text_utils.remove_whitespace(description)
        self.runtime_exceptions.append(description)

    def network_request_will_be_sent(self, params):
        request_id = params["requestId"]
        request_time = params["timestamp"]
        new_request = {
            "time_start": request_time,
            "resource_url": params["request"]["url"],
            "from_cache": None,
            "http_status": None,
            "error_name": None,
            "time_end": None,
            "data_received": None
        }

        # if first request made on this page
        if not self.network_requests:
            new_request["is_main_resource"] = True  # this first accessed resource is main
            self.general["main_request_id"] = request_id  # DevTools internal ID of first request
            self.general["time_start"] = request_time

        self.network_requests[request_id] = new_request

    def network_response_received(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        response = params["response"]
        self._update_time_end_if_later(request_id, params["timestamp"])
        self._update_data_received(request_id, response["encodedDataLength"])
        self._set_cache_status_if_not_set(request_id, response["fromDiskCache"])
        http_status = response["status"]
        self.network_requests[request_id]["http_status"] = http_status
        self._set_main_request_http_status(request_id, http_status)

    # responseReceived and loadingFinished can arrive in different order, we need the latest time, biggest size
    # loadingFinished is used only to provide more accurate data
    def network_loading_finished(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        self._update_time_end_if_later(request_id, params["timestamp"])
        self._update_data_received(request_id, params["encodedDataLength"])

    # this is not the same cache type as Response[fromDiskCache]
    def network_request_served_from_cache(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        self.network_requests[request_id]["from_cache"] = True

    def network_loading_failed(self, params):
        request_id = params["requestId"]
        if request_id not in self.network_requests:
            return
        self._update_time_end_if_later(request_id, params["timestamp"])
        self._set_cache_status_if_not_set(request_id, False)
        if self.network_requests[request_id]["http_status"] is None:
            self.network_requests[request_id]["http_status"] = 0
        if not self.network_requests[request_id]["data_received"]:
            self.network_requests[request_id]["data_received"] = 0
        if "blockedReason" in params:
            self.network_requests[request_id]["error_name"] = "blocked:%s" % params["blockedReason"]
        else:
            self.network_requests[request_id]["error_name"] = params["errorText"]

    def page_dom_content_event_fired(self, params):
        if not self.general["time_dom_content"]:
            self.general["time_dom_content"] = params["timestamp"]

    def page_load_event_fired(self, params):
        if not self.general["time_load"]:
            self.general["time_load"] = params["timestamp"]

    def log_entry_added(self, params):
        entry = params["entry"]
        log = {
            "level": entry["level"],
            "source": entry["source"],
            "text": text_utils.remove_whitespace(entry["text"])
        }
        self.console_logs.append(log)

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

    def _set_main_request_http_status(self, request_id, http_status):
        if request_id == self.general["main_request_id"]:
            self.main_request_http_status = http_status
