import time


class RemoteDebugActions(object):
    def __init__(self, devtools_protocol):
        self._devtools_protocol = devtools_protocol

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
            self.execute_javascript(javascript)
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
        result = self.execute_javascript(
            "document.querySelector('%s');" % element_css
        )
        return result["subtype"] != "null"

    def scroll_to_bottom(self):
        self.execute_javascript(
            "window.scrollTo(0,document.body.scrollHeight);"
        )

    def execute_javascript(self, expression):
        result = self._devtools_protocol.send_command("Runtime.evaluate", {"expression": expression})
        return result["result"]
