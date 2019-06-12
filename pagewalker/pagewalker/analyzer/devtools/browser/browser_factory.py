from pagewalker.config import config
from . import chrome_desktop, chrome_mobile_emulator, chrome_android


def get_new_browser():
    if config.android_browser_enabled:
        return chrome_android.ChromeAndroid
    elif config.mobile_emulation_enabled:
        return chrome_mobile_emulator.ChromeMobileEmulator
    else:
        return chrome_desktop.ChromeDesktop


def get_running_browser(browser_data):
    if "Android-Package" in browser_data:
        return chrome_android.ChromeAndroid
    else:
        return chrome_desktop.ChromeDesktop
