import time
from pagewalker.utilities import error_utils


class RemoteDebugJavascript(object):
    def __init__(self, devtools_protocol):
        self._devtools_protocol = devtools_protocol

    @property
    def screen_width(self):
        return self._return_value("window.screen.availWidth;")

    @property
    def screen_height(self):
        return self._return_value("window.screen.availHeight;")

    def set_text(self, element_css, text):
        javascript = "document.querySelector('%s').value = '%s';" % (element_css, text)
        return self._execute_if_element_present(element_css, javascript)

    def click(self, element_css):
        javascript = "document.querySelector('%s').click();" % element_css
        return self._execute_if_element_present(element_css, javascript)

    def submit(self, element_css):
        javascript = "document.querySelector('%s').submit();" % element_css
        return self._execute_if_element_present(element_css, javascript)

    def _execute_if_element_present(self, element_css, javascript):
        if self.is_element_present(element_css):
            self._execute(javascript)
            return True
        return False

    def wait_element_present(self, element_css, timeout):
        poll_frequency = 0.5
        end_time = time.time() + timeout
        while True:
            if self.is_element_present(element_css):
                return True
            time.sleep(poll_frequency)
            if time.time() > end_time:
                break
        return False

    def is_element_present(self, element_css):
        result = self._execute(
            "document.querySelector('%s');" % element_css
        )
        return result["subtype"] != "null"

    def scroll_to_bottom(self):
        self._execute("window.scrollTo(0,document.body.scrollHeight);")

    def _return_value(self, expression):
        result = self._execute(expression)
        if "value" not in result:
            msg = "JavaScript execution failed"
            msg += "\nExpression: %s" % expression
            msg += "\nResult data: %s" % result
            error_utils.exit_with_message(msg)
        return result["value"]

    def _execute(self, expression):
        result = self._devtools_protocol.send_command("Runtime.evaluate", {"expression": expression})
        return result["result"]
