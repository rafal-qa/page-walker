from os import path
from pagewalker import get_project_root
from pagewalker.config import platform_defaults


root = get_project_root()
start_url = None
max_number_pages = 10
pages_list_file = None
pages_list_only = True
wait_time_after_load = 1
scroll_after_load = True
window_size = "1366x768"
chrome_headless = False
chrome_close_on_finish = True
chrome_debugging_port = 9222
chrome_timeout = 30
chrome_data_dir = path.join(root, "temp", "chrome_data")
chrome_binary = platform_defaults.chrome_binary
chrome_ignore_cert = False
mobile_emulation_enabled = False
mobile_window_size = "360x640"
mobile_user_agent = "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) " \
                    "Chrome/74.0.3729.169 Mobile Safari/537.36"
android_browser_enabled = True
android_adb_binary = path.join(root, "lib", "platform-tools", platform_defaults.adb_binary_file)
http_basic_auth_data = None
custom_cookies_file = None
custom_cookies_data = None
initial_actions_file = None
initial_actions_data = None
initial_actions_url = None
validator_enabled = True
validator_check_css = True
validator_show_warnings = True
validator_html_dir = path.join(root, "temp", "validator")
validator_vnu_jar = path.join(root, "lib", "vnu", "vnu.jar")
java_binary = platform_defaults.java_binary
java_stack_size = 4096
check_external_links = True
check_external_links_timeout = 10
check_external_links_threads = 4
domain_blacklist_enabled = True
domain_blacklist_cache_expiry = 24
domain_blacklist_url = "https://raw.githubusercontent.com/rafal-qa/page-walker/master/lib/pagewalker/domain_lists.json"
domain_blacklist_auto_update = True
domain_blacklist_dir = path.join(root, "temp", "domain_blacklist")
domain_blacklist_file = path.join(domain_blacklist_dir, "current_list.txt")
requests_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                      "Chrome/75.0.3770.80 Safari/537.36"
output_data = path.join(root, "output")
current_data_dir = None
current_data_subdir = None
ini_file = path.join(root, "config", "main.ini")
