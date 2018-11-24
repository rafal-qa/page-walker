from os import path
from pagewalker.config import platform_defaults, root_path


root = root_path.get()
start_url = None
max_number_pages = 10
pages_list_file = None
pages_list_only = True
wait_time_after_load = 1
scroll_after_load = True
keep_previous_data = True
window_size = "1366x768"
chrome_headless = False
chrome_close_on_finish = True
chrome_debugging_port = 9222
chrome_timeout = 30
chrome_data_dir = path.join(root, "temp", "chrome_data")
chrome_binary = platform_defaults.chrome_binary()
chrome_ignore_cert = False
user_agent = "Mozilla/5.0 AppleWebKit/537.36 Chrome/70.0.3538.77"
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
java_binary = platform_defaults.java_binary()
java_stack_size = 4096
check_external_links = True
check_external_links_timeout = 10
domain_blacklist_enabled = True
domain_blacklist_cache_expiry = 24
domain_blacklist_url = "https://raw.githubusercontent.com/rafal-qa/page-walker/master/lib/pagewalker/domain_lists.json"
domain_blacklist_auto_update = True
domain_blacklist_dir = path.join(root, "config", "domain_blacklist")
domain_blacklist_file = path.join(domain_blacklist_dir, "current_list.txt")
output_data = path.join(root, "output")
current_data_dir = None
current_data_subdir = None
ini_file = path.join(root, "config", "default.ini")
