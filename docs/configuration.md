# Configuration

### Interactive mode

You can run Page Walker without any parameters. It's the same as double-clicking standalone release on Windows. You will be asked to provide URL of website to test, etc.

### 3-level configuration

1. Hard-coded defaults. Chrome browser location depends on operating system.
2. Configuration file `config/main.ini`. It overwrites hard-coded defaults. If parameter is empty or omitted, hard-coded default will be used. Use it to configure your environment: custom location of Chrome, Java, parameters that you do not plan to change.
3. Command line arguments. It overwrites hard-coded defaults and configuration file parameters. Run with `-h` parameter to see all available options.

### Configurable parameters

| Command_line argument | `config/main.ini` | Default value | Description |
| --------------------- | ----------------- | ------------- | ----------- |
| `-u` or `--url` | `start_url` | n/a | URL of first page to visit, with `http(s)://`. |
| `-p` or `--pages` | `max_number_pages` | 10 | Maximum number of pages to visit. |
| `--headless` | `chrome_headless` | no | [yes/no] Run Chrome in headless mode. |
| `--pages-list` | `pages_list_file` | n/a | [Optional] File containing list of pages to visit. Pages relative to main domain, starting with `/`. |
| `--list-only` | `pages_list_only` | yes | [yes/no] Visit all and only pages from file, regardless of _maximum number of pages_ value. Option has no effect if file with pages list is not set. |
| `--wait-after` | `wait_time_after_load` | 1 | Wait time (in seconds) after page was loaded (browser received `Load` event). Even after `Load` event the browser usually downloads some data so it's better to set it for 1-3 seconds.
| `--scroll-after` | `scroll_after_load` | yes | [yes/no] Scroll to bottom of page after page was loaded, before _wait time_. While scrolling browser can receive more events and data to analyze. |
| n/a | `window_size` | 1366x768 | Size of desktop browser window. |
| `--close-on-finish` | `chrome_close_on_finish` | yes | [yes/no] Close browser after finish. For debugging you can set to _no_ to interact with browser after app has finished running. |
| | **CHROME** | | |
| `--chrome-port` | `chrome_debugging_port` | 9222 | Chrome remote debugger port number. To run multiple tests in parallel set different port for every instance. |
| `--chrome-timeout` | `chrome_timeout` | 30 | Chrome connection timeout in seconds. How long to wait for `Load` event. |
| `--chrome-binary` | `chrome_binary` | System dependent, auto-detected on Windows | Path to Chrome executable file. |
| `--chrome-ignore-cert` | `chrome_ignore_cert` | no | [yes/no] Ignore SSL errors. Set to _yes_ if you want to test a website with invalid SSL certificate. |
| | **MOBILE EMULATION** | | |
| `--mobile-emulation` | `mobile_emulation_enabled` | no | [yes/no] Use mobile browser emulation. |
| n/a | `mobile_window_size` | 360x640 | Mobile screen size. |
| n/a | `mobile_user_agent` | see: [config.py](../pagewalker/pagewalker/config/config.py) | Mobile User Agent. |
| | **ANDROID DEVICE** | | |
| `--android-browser` | `android_browser_enabled` | no | [yes/no] Use Chrome for Android on connected device. |
| n/a | `android_adb_binary` | `lib/platform-tools/adb` | Path to Android Debug Bridge (adb) executable. |
| | **AUTH, COOKIES** | | |
| `--http-auth` | `http_basic_auth_data` | n/a | HTTP Basic authentication credentials in format `login:password` |
| `--cookies-file` | `custom_cookies_file` | n/a | Config file with custom cookies definition, more: [Custom cookies](docs/custom-cookies.md) |
| `--initial-actions-file` | `initial_actions_file` | n/a | Config file with initial actions definition, more: [Initial actions](docs/initial-actions.md) |
| `--initial-actions-url` | `initial_actions_url` | the same as `start_url` | URL of the page on which to perform initial actions. Option has no effect if `initial_actions_file` was not set. |
| | **HTML VALIDATOR** | | |
| `--validate` | `validator_enabled` | yes | [yes/no] Enable HTML validator. Set to _no_ if you don't have Java installed. |
| n/a | `validator_check_css` | yes | [yes/no] Check also inline CSS. Option has no effect if HTML validator is disabled. |
| n/a | `validator_show_warnings` | yes | [yes/no] Report also warnings (in addition to errors). Option has no effect if HTML validator is disabled. |
| n/a | `validator_vnu_jar` | `lib/vnu/vnu.jar` | Path to vNu HTML validator JAR file. |
| n/a | `java_binary` | System dependent | Path to Java executable file. To use custom Java unpacked to `lib` directory, set for example to `lib/jre{ver}/bin/java` |
| n/a | `java_stack_size` | 4096 | Java stack size [KB]. If you experience stack overflow errors while validating extremely large HTML page, increase it. |
| | **BROKEN LINKS** | | |
| `--check-links` | `check_external_links` | yes | [yes/no] Check HTTP response status of external links. |
| n/a | `check_external_links_timeout` | 10 | External links checking connection timeout in seconds. | 
| n/a | `check_external_links_threads` | 4 | Check links in multiple threads. |
| | **DOMAIN BLACKLIST** | | |
| `--domain-blacklist` | `domain_blacklist_enabled` | yes | [yes/no] Check if domains are blacklisted due to malware, scam. |
| n/a | `domain_blacklist_cache_expiry` | 24 | Domain blacklist cache expiry in hours. |
| n/a | `domain_blacklist_auto_update` | yes | Domain blacklist auto update. |
| n/a | `domain_blacklist_url` | [URL](https://raw.githubusercontent.com/rafal-qa/page-walker/master/lib/pagewalker/domain_lists.json) | URL with current domain lists. |
| | **INFORMATION** | | |
| `-v` or `--version` | n/a | n/a| Show app and Python version and exit. |
| `-h` or `--help` | n/a | n/a | Show all command line options. |

#### Boolean values

For boolean values (yes/no) you can also use:
* instead of `yes`: `y`, `true`, `1`
* instead of `no`: `n`, `false`, `0`
