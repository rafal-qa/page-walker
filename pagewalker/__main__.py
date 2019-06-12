import argparse
from pagewalker import print_version
from pagewalker.utilities import console_utils, error_utils, prepare_directories
from pagewalker.analyzer import analyzer, http_headers_analyzer
from pagewalker.analyzer.blacklist import blacklist_downloader
from pagewalker.report import report
from pagewalker.config import config_validator, java_checker, config
from pagewalker.config.file_parser import main_config_parser, cookies_config_parser, initial_actions_config_parser


main_config_parser.MainConfigParser().apply()

argparse_types = config_validator.ConfigValidatorArgparse()
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
                    help="File containing list of pages to visit (pages relative to main domain)",
                    type=argparse_types.file)
parser.add_argument("--list-only", dest="pages_list_only",
                    help="Visit all and only pages from file, if file provided (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--wait-after", dest="wait_time_after_load",
                    help="Wait time in seconds after page was loaded",
                    type=argparse_types.positive_integer)
parser.add_argument("--scroll-after", dest="scroll_after_load",
                    help="Scroll to bottom of page after page was loaded (yes/no)",
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
parser.add_argument("--mobile-emulation", dest="mobile_emulation_enabled",
                    help="Enable mobile browser emulation on Chrome Desktop (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--android-browser", dest="android_browser_enabled",
                    help="Run tests on Chrome for Android on connected device (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--http-auth", dest="http_basic_auth_data",
                    help="HTTP authentication credentials in format login:password")
parser.add_argument("--cookies-file", dest="custom_cookies_file",
                    help="Config file with custom cookies definition",
                    type=argparse_types.file)
parser.add_argument("--initial-actions-file", dest="initial_actions_file",
                    help="Config file with initial actions definition",
                    type=argparse_types.file)
parser.add_argument("--initial-actions-url", dest="initial_actions_url",
                    help="URL of the page on which to perform initial actions (default the same as 'start_url')",
                    type=argparse_types.url)
parser.add_argument("--validate", dest="validator_enabled",
                    help="Enable HTML validator (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--check-links", dest="check_external_links",
                    help="Check external links (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--domain-blacklist", dest="domain_blacklist_enabled",
                    help="Check if domains are blacklisted due to malware, scam (yes/no)",
                    type=argparse_types.boolean)
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
    config_types = config_validator.ConfigValidatorInteractive()
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

if config.custom_cookies_file:
    cookies_config_parser.CookiesConfigParser().apply()

if config.initial_actions_file:
    initial_actions_config_parser.InitialActionsConfigParser().apply()

if config.domain_blacklist_enabled:
    blacklist_downloader.BlacklistDownloader().update()

http_headers_analyzer.HTTPHeadersAnalyzer(config.chrome_timeout).check_valid_first_url()

prepare_directories.PrepareDirectories().create()

analyzer.Analyzer().start_new_analysis()

report.Report().generate_html()

console_utils.finish()
