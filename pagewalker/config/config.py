from os import path
from pagewalker.config import platform_defaults


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
chrome_data_dir = path.join("temp", "chrome_data")
chrome_binary = platform_defaults.chrome_binary()
chrome_ignore_cert = False
user_agent = "Mozilla/5.0 AppleWebKit/537.36 Chrome/70.0.3538.77"
http_basic_auth_data = None
validator_enabled = True
validator_check_css = True
validator_show_warnings = True
validator_html_dir = path.join("temp", "validator")
validator_vnu_jar = path.join("lib", "vnu", "vnu.jar")
java_binary = platform_defaults.java_binary()
java_stack_size = 4096
check_external_links = True
check_external_links_timeout = 10
output_data = "output"
current_data_dir = None
current_data_subdir = None
sqlite_file = None
ini_file = path.join("config", "default.ini")
