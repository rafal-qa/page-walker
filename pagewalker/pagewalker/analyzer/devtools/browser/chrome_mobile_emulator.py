from .chrome_desktop import ChromeDesktop
from pagewalker.utilities import error_utils
from pagewalker.config import config


class ChromeMobileEmulator(ChromeDesktop):
    def _print_start_message(self):
        print("[INFO] Running Chrome in mobile emulation mode, saving output to %s" % self._log_file_name)

    def _enable_mobile_emulation(self):
        result = self._devtools_protocol.send_command("Emulation.canEmulate")
        if "result" not in result or not result["result"]:
            error_utils.exit_with_message("Emulation is not supported in DevTools protocol")
        self._devtools_protocol.send_command("Emulation.setDeviceMetricsOverride", self._device_metrics)
        self._devtools_protocol.send_command("Emulation.setUserAgentOverride", {"userAgent": config.mobile_user_agent})

    @property
    def _device_metrics(self):
        width, height = config.mobile_window_size.split("x")
        return {
            "width": int(width),
            "height": int(height),
            "deviceScaleFactor": 0,
            "mobile": True
        }

    @property
    def user_agent(self):
        return config.mobile_user_agent
