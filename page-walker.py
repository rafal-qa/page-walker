import argparse
from os import path
from pagewalker.config import config_validator, config_file_parser, java_checker
from pagewalker.config.config_default import main_config
from pagewalker import prepare_directories
from pagewalker import get_versions
from pagewalker.utilities import console_utils, error_utils
from pagewalker.analyzer import analyzer, http_headers_analyzer
from pagewalker.report import report


config_ini = config_file_parser.ConfigFileParser("config/default.ini")
main_config = config_ini.apply_config(main_config)

argparse_types = config_validator.ConfigValidator("argparse")
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="Full URL of first page to visit (http://example.com/page.html)",
                    type=argparse_types.url)
parser.add_argument("-p", "--pages", help="Maximum number of pages to visit",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("-l", "--headless", help="Run Chrome in headless mode (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--pages-list", help="File containing list of pages to visit (pages relative to main domain)")
parser.add_argument("--list-only", help="Visit all and only pages from file, if file provided (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--wait-after", help="Wait time in seconds after page was loaded",
                    type=argparse_types.positive_integer)
parser.add_argument("--scroll-after", help="Scroll to bottom of page after page was loaded (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--keep-previous", help="Keep data from previous program run (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--window-size", help="Size of browser window in format [width]x[height]",
                    type=argparse_types.dimension)
parser.add_argument("--close-on-finish", help="Close browser after finish (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--chrome-port", help="Chrome remote debugger port number",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("--chrome-timeout", help="Chrome connection timeout in seconds",
                    type=argparse_types.positive_non_zero_integer)
parser.add_argument("--chrome-binary", help="Path to Chrome executable file")
parser.add_argument("--chrome-ignore-cert", help="Ignore SSL errors (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--validate", help="Enable HTML validator (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--check-css", help="Check also CSS if HTML validator is enabled (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--validator-warnings", help="Report also warnings if HTML validator is enabled (yes/no)",
                    type=argparse_types.boolean)
parser.add_argument("--java-binary", help="Path to Java executable file")
parser.add_argument("-v", "--version", help="Show Page Walker and Python version", action='store_true')
args = parser.parse_args()

if args.version:
    versions = get_versions()
    print("Page Walker: %s" % versions["app"])
    print("Python: %s (%s-bit)" % (versions["python"], versions["arch"]))
    console_utils.finish(True)

if args.url is not None:
    main_config["start_url"] = args.url
if args.pages is not None:
    main_config["max_number_pages"] = args.pages
if args.headless is not None:
    main_config["chrome_headless"] = args.headless
if args.pages_list is not None:
    main_config["pages_list_file"] = args.pages_list
if args.list_only is not None:
    main_config["pages_list_only"] = args.list_only
if args.wait_after is not None:
    main_config["wait_time_after_load"] = args.wait_after
if args.scroll_after is not None:
    main_config["scroll_after_load"] = args.scroll_after
if args.keep_previous is not None:
    main_config["keep_previous_data"] = args.keep_previous
if args.window_size is not None:
    main_config["window_size"] = args.window_size
if args.close_on_finish is not None:
    main_config["chrome_close_on_finish"] = args.close_on_finish
if args.chrome_port is not None:
    main_config["chrome_debugging_port"] = args.chrome_port
if args.chrome_timeout is not None:
    main_config["chrome_timeout"] = args.chrome_timeout
if args.chrome_binary is not None:
    main_config["chrome_binary"] = args.chrome_binary
if args.chrome_ignore_cert is not None:
    main_config["chrome_ignore_cert"] = args.chrome_ignore_cert
if args.validate is not None:
    main_config["validator_enabled"] = args.validate
if args.check_css is not None:
    main_config["validator_check_css"] = args.check_css
if args.validator_warnings is not None:
    main_config["validator_show_warnings"] = args.validator_warnings
if args.java_binary is not None:
    main_config["java_binary"] = args.java_binary

if main_config["validator_enabled"]:
    check_java = java_checker.JavaChecker(main_config["java_binary"])
    if not check_java.is_installed():
        main_config["validator_enabled"] = False

if console_utils.interactive_mode:
    config_types = config_validator.ConfigValidator("interactive")
    url_default = main_config["start_url"] if main_config["start_url"] else None
    main_config["start_url"] = config_types.url(
        console_utils.read_input("Start URL to test", url_default)
    )
    main_config["max_number_pages"] = config_types.positive_non_zero_integer(
        console_utils.read_input("Number of pages to visit", main_config["max_number_pages"])
    )
    headless_default = "y" if main_config["chrome_headless"] else "n"
    main_config["chrome_headless"] = config_types.boolean(
        console_utils.read_input("Headless mode (y/n)", headless_default)
    )

if not main_config["start_url"]:
    error_utils.exit_with_message("Start URL is required")

http_headers = http_headers_analyzer.HTTPHeadersAnalyzer(main_config["chrome_timeout"])
http_headers.check_200_ok_html(main_config["start_url"])

make_dirs = prepare_directories.PrepareDirectories(main_config["output_data"], main_config["keep_previous_data"])
make_dirs.create()
main_config["current_data_dir"] = make_dirs.get_current_dir()
main_config["sqlite_file"] = path.join(main_config["current_data_dir"], "data.db")

analyzer = analyzer.Analyzer(main_config)
analyzer.start_new_analysis()

make_report = report.Report(main_config["sqlite_file"], main_config["current_data_dir"])
make_report.generate_html()

current_subdir = make_dirs.get_current_subdir()
make_report.redirect_to_latest(main_config["output_data"], current_subdir)

console_utils.finish()
