try:
    import winreg  # Python 3
except ImportError:
    import _winreg as winreg  # Python 2
    FileNotFoundError = WindowsError


class WindowsRegistry(object):
    def __init__(self):
        self.hkeys = {
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT
        }

    def chrome_exe_path(self):
        install_location = self._find_chrome_in_install_location()
        if install_location:
            return install_location
        chrome_html = self._find_chrome_in_chrome_html()
        if chrome_html:
            return chrome_html
        return False

    def _find_chrome_in_install_location(self):
        hkeys = ["HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE"]
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"
        value_name = "InstallLocation"
        for hkey in hkeys:
            value = self._read_value_from_key(hkey, sub_key, value_name)
            if value:
                return "%s\chrome.exe" % value
        return False

    # "C:\Program Files\Google\Chrome\Application\chrome.exe" -- "%1"
    def _find_chrome_in_chrome_html(self):
        hkey = "HKEY_CLASSES_ROOT"
        sub_key = "ChromeHTML\\shell\\open\\command"
        value_name = None
        value = self._read_value_from_key(hkey, sub_key, value_name)
        if value:
            parts = str(value).split('"')
            return parts[1] if len(parts) > 1 else False
        return False

    def _read_value_from_key(self, hkey, sub_key, value_name):
        try:
            key = winreg.OpenKey(self.hkeys[hkey], sub_key)
            value = winreg.QueryValueEx(key, value_name)[0]
        except FileNotFoundError:
            value = False
        return value
