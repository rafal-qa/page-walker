import platform
from os import path
from pagewalker.utilities import error_utils


if platform.system() == "Windows":
    from pagewalker.utilities import windows_registry
    registry = windows_registry.WindowsRegistry()
    chrome_binary = registry.chrome_exe_path()
    if not chrome_binary:
        error_utils.exit_with_message("Path to chrome.exe not found. Please provide custom file location.")
    java_binary = "Java"
else:
    chrome_binary = "chromium-browser"
    java_binary = "java"

main_config = {
    "start_url": None,
    "max_number_pages": 10,
    "pages_list_file": None,
    "pages_list_only": True,
    "wait_time_after_load": 1,
    "scroll_after_load": True,
    "keep_previous_data": True,
    "window_size": "1366x768",
    "chrome_headless": False,
    "chrome_close_on_finish": True,
    "chrome_debugging_port": 9222,
    "chrome_timeout": 30,
    "chrome_data_dir": path.join("temp", "chrome_data"),
    "chrome_binary": chrome_binary,
    "chrome_ignore_cert": False,
    "validator_enabled": True,
    "validator_check_css": True,
    "validator_show_warnings": True,
    "validator_html_dir": path.join("temp", "validator"),
    "validator_vnu_jar": path.join("lib", "vnu", "vnu.jar"),
    "java_binary": java_binary,
    "java_stack_size": 4096,
    "output_data": "output",
    "current_data_dir": None,
    "sqlite_file": None
}
