from .devtools import remote_debug_javascript
from pagewalker.utilities import error_utils
from pagewalker.config import config


class InitialActions(object):
    def __init__(self, remote_debug, devtools_protocol):
        self._remote_debug = remote_debug
        self._javascript = remote_debug_javascript.RemoteDebugJavascript(devtools_protocol)
        self._apply()

    def _apply(self):
        self._open_url()
        for action_data in config.initial_actions_data:
            self._single_step(action_data)

    def _single_step(self, action_data):
        step = action_data["step"]
        print("[INFO] Initial action: %s" % step)
        action = action_data["action"]
        element_css = action_data["css"]
        if action == "set_text":
            found = self._javascript.set_text(element_css, action_data["text"])
        elif action == "click":
            found = self._javascript.click(element_css)
        elif action == "submit":
            found = self._javascript.submit(element_css)
        elif action == "wait_element_present":
            timeout = int(action_data["timeout"])
            found = self._javascript.wait_element_present(element_css, timeout)
        else:
            found = False
        if not found:
            self._element_not_found(step, element_css)

    def _open_url(self):
        url = config.initial_actions_url if config.initial_actions_url else config.start_url
        print("[INFO] Initial action: %s" % url)
        self._remote_debug.open_url(url)

    def _element_not_found(self, step, element_css):
        self._remote_debug.end_session()
        msg = "Initial actions step [%s] failed" % step
        msg += "\nElement not found: %s" % element_css
        error_utils.exit_with_message(msg)
