import time
from subprocess import Popen, PIPE
from pagewalker.utilities import text_utils, error_utils
from pagewalker.config import config
from .browser_abstract import BrowserAbstract


class ChromeAndroid(BrowserAbstract):
    _adb_devices_list = []
    _device_model = None

    def _start_browser(self):
        self._adb_kill_server()
        self._update_devices_list()
        self._assert_one_device_only()
        self._handle_device_offline()
        self._wait_for_authorization()
        self._get_device_model()
        self._activate_connection_to_device()

    @property
    def _devices_count(self):
        return len(self._adb_devices_list)

    @property
    def _offline(self):
        return "offline" in self._device_info_parts

    @property
    def _authorized(self):
        return "unauthorized" not in self._device_info_parts

    @property
    def _device_info_parts(self):
        return self._adb_devices_list[0].split()

    def _adb_kill_server(self):
        self._exec_adb(["kill-server"])

    def _update_devices_list(self):
        cmd_output = self._exec_adb(["devices", "-l"])
        output_lines = cmd_output.split("\n")
        self._adb_devices_list = output_lines[1:]

    def _assert_one_device_only(self):
        if self._devices_count == 0:
            error_utils.exit_with_message("No connected Android devices found")
        elif self._devices_count > 1:
            msg = "%s connected Android devices found" % self._devices_count
            msg += "\nPlease connect only one and try again"
            error_utils.exit_with_message(msg)

    def _handle_device_offline(self):
        if self._offline:
            print("[WARN] Connected device detected as 'offline', trying once again...")
            self._adb_kill_server()
            self._update_devices_list()
            if self._offline:
                msg = "Connected device detected as 'offline'"
                msg += "\nTry disconnect USB and connect again"
                error_utils.exit_with_message(msg)

    def _wait_for_authorization(self):
        if self._authorized:
            return
        timeout = 60
        msg = "\n*** Waiting max. %s seconds for authorization ***" % timeout
        msg += "\nAccept the connection from this computer on your Android device\n"
        print(msg)
        start = time.time()
        while time.time() - start < timeout:
            if self._authorized:
                return
            else:
                time.sleep(1)
                self._update_devices_list()
        error_utils.exit_with_message("Authorization timeout")

    def _get_device_model(self):
        model = self._get_device_property("model")
        if not model:
            msg = "Unable to get device model information from ADB output:\n" + self._adb_devices_list[0]
            error_utils.exit_with_message(msg)
        self._device_model = model

    def _get_device_property(self, property_name):
        property_name += ":"
        for device_info_part in self._adb_devices_list[0].split():
            if device_info_part.startswith(property_name):
                return device_info_part.replace(property_name, "")
        return None

    def _activate_connection_to_device(self):
        port = "tcp:%s" % config.chrome_debugging_port
        self._exec_adb(["forward", port, "localabstract:chrome_devtools_remote"])

    def _exec_adb(self, parameters):
        command_parts = [config.android_adb_binary] + parameters
        try:
            p = Popen(command_parts, stdout=PIPE, stderr=PIPE)
        except OSError:
            self._adb_not_found()
            return
        out, err = p.communicate()
        if p.returncode:
            msg = " ".join(command_parts) + "\n" + text_utils.bytes_to_string(err)
            error_utils.exit_with_message(msg)
        return text_utils.bytes_to_string(out)

    def _adb_not_found(self):
        message = "Android Debug Bridge (adb) was not found at location:\n%s" % config.android_adb_binary
        message += "\n\nYou can provide custom adb location in file:\n%s (option 'android_adb_binary')" % config.ini_file
        error_utils.exit_with_message(message)

    def _print_start_message(self):
        print("[INFO] Running Chrome for Android on connected device (model: %s)" % self._device_model)

    def _clear_browser_data(self):
        self._clear_browser_cache()
        self._clear_page_only_cookies()

    def _clear_browser_cache(self):
        self._devtools_protocol.send_command("Network.clearBrowserCache")

    def _clear_page_only_cookies(self):
        cookies = self._devtools_protocol.get_cookies_for_url(config.start_url)
        if not cookies:
            return
        print("[INFO] Deleting %s previous cookies" % len(cookies))
        for cookie in cookies:
            data = {
                "name": cookie["name"],
                "domain": cookie["domain"],
                "path": cookie["path"]
            }
            self._devtools_protocol.send_command("Network.deleteCookies", data)

    def close(self):
        self._adb_kill_server()

    def close_previously_unclosed(self):
        msg = "Chrome on Android device is already connected on port %s" % config.chrome_debugging_port
        msg += "\nDisconnecting it now..."
        error_utils.show_warning(msg)
        self.close()
