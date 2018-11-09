import argparse
from os import path
from pagewalker.config import config_validator, config_file_parser, java_checker
from pagewalker import prepare_directories, print_version
from pagewalker.utilities import console_utils, error_utils
from pagewalker.analyzer import analyzer, http_headers_analyzer
from pagewalker.report import report
from pagewalker.config import config


config_file_parser.ConfigFileParser().apply()

argparse_types = config_validator.ConfigValidator("argparse")
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", dest="start_url",
                    help="Full URL of first page to visit (http://example.com/page.html)",
                    type=argparse_types.url)
parser.add_argument("-p", "--pages", dest="max_number_pages",
                    help="Maximum number of pages to visit",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("-l", "--headless", dest="chrome_headless",
                    help="Run Chrome in headless mode (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--pages-list", dest="pages_list_file",
                    help="File containing list of pages to visit (pages relative to main domain)")
parser.add_argument("--list-only", dest="pages_list_only",
                    help="Visit all and only pages from file, if file provided (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--wait-after", dest="wait_time_after_load",
                    help="Wait time in seconds after page was loaded",
                    type=argparse_types.positive_integer)
parser.add_argument("--scroll-after", dest="scroll_after_load",
                    help="Scroll to bottom of page after page was loaded (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--keep-previous", dest="keep_previous_data",
                    help="Keep data from previous program run (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--window-size", dest="window_size",
                    help="Size of browser window in format [width]x[height]",
                    type=argparse_types.dimension)
parser.add_argument("--close-on-finish", dest="chrome_close_on_finish",
                    help="Close browser after finish (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--chrome-port", dest="chrome_debugging_port",
                    help="Chrome remote debugger port number",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("--chrome-timeout", dest="chrome_timeout",
                    help="Chrome connection timeout in seconds",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("--chrome-binary", dest="chrome_binary",
                    help="Path to Chrome executable file")
parser.add_argument("--chrome-ignore-cert", dest="chrome_ignore_cert",
                    help="Ignore SSL errors (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--http-auth", dest="http_basic_auth_data",
                    help="HTTP authentication credentials in format login:password")
parser.add_argument("--validate", dest="validator_enabled",
                    help="Enable HTML validator (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--check-css", dest="validator_check_css",
                    help="Check also CSS if HTML validator is enabled (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--validator-warnings", dest="validator_show_warnings",
                    help="Report also warnings if HTML validator is enabled (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--java-binary", dest="java_binary",
                    help="Path to Java executable file")
parser.add_argument("--check-links", dest="check_external_links",
                    help="Check external links (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--check-links-timeout", dest="check_external_links_timeout",
                    help="Connection timeout in seconds",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("-v", "--version", help="Show Page Walker and Python version", action='store_true')
args = parser.parse_args()

if args.version:
    print_version()

for config_name in vars(args):
    config_value = getattr(args, config_name)
    if config_value is not None:
        setattr(config, config_name, config_value)

if config.validator_enabled:
    java_checker.JavaChecker().disable_validator_if_no_java()

if console_utils.interactive_mode:
    config_types = config_validator.ConfigValidator("interactive")
    config.start_url = config_types.url(
        console_utils.read_input("Start URL to test", config.start_url)
    )
    config.max_number_pages = config_types.positive_non_zero_integer(
        console_utils.read_input("Number of pages to visit", config.max_number_pages)
    )
    headless_default = "y" if config.chrome_headless else "n"
    config.chrome_headless = config_types.boolean(
        console_utils.read_input("Headless mode (y/n)", headless_default)
    )

if not config.start_url:
    error_utils.exit_with_message("Start URL is required")

http_headers = http_headers_analyzer.HTTPHeadersAnalyzer(config.chrome_timeout)
http_headers.check_200_ok_html(config.start_url)

prepare_directories.PrepareDirectories().create()
config.sqlite_file = path.join(config.current_data_dir, "data.db")

analyzer.Analyzer().start_new_analysis()

report.Report().generate_html()

console_utils.finish()
