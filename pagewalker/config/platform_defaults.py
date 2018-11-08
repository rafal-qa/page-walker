import platform
from pagewalker.utilities import error_utils


def java_binary():
    return "Java" if _is_windows() else "java"


def chrome_binary():
    if _is_windows():
        from pagewalker.utilities import windows_registry
        registry = windows_registry.WindowsRegistry()
        chrome = registry.chrome_exe_path()
        if not chrome:
            error_utils.exit_with_message("Path to chrome.exe not found. Please provide custom file location.")
        return chrome
    else:
        return "chromium-browser"


def _is_windows():
    return platform.system() == "Windows"
