# Page Walker

*Zero-configuration test automation tool.*

Page Walker crawls a website using Google Chrome browser, analyze data from Developer tools and performs other tests.

The result is an interactive report - [see example report](https://rafal-qa.com/pagewalker-example-report/).

### Types of detected defects

* Network errors while loading page
* Requests to blacklisted domains (malware)
* JavaScript runtime exceptions
* DevTools Console errors
* Broken links, including links to blacklisted domains
* HTML/CSS validation errors - before and after JavaScript execution

### Links

* Project homepage: [rafal-qa.com/page-walker/](https://rafal-qa.com/page-walker/)
* Source code: [github.com/rafal-qa/page-walker](https://github.com/rafal-qa/page-walker)
* Stand-alone executables: [github.com/rafal-qa/page-walker/releases](https://github.com/rafal-qa/page-walker/releases)

# Table of contents

* [Getting started](#getting-started)
* [Running from source code](#running-from-source-code)
* [Features](#features)
* [Configuration](#configuration)
* [Limitations and known problems](#limitations-and-known-problems)
* [More information](#more-information)
* [TODO](#todo)
* [License](#license)
* [Acknowledgments](#acknowledgments)

# Getting started

For quick start use [stand-alone version](https://github.com/rafal-qa/page-walker/releases). It's a compiled application with all dependencies. No installation or configuration needed (it works on reasonable defaults). Just run.

### Prerequisites

* Current Chrome/Chromium browser (or at least version 66) must be installed.
* For using HTML validator Java 8 (or newer) is required. If you disable HTML validation, it works without Java. [Download Java 8](http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html).

### Stand-alone version

You don't need anything else. [Download Page Walker](https://github.com/rafal-qa/page-walker/releases), unpack and run.

#### Windows

Double-click `page-walker` and it will run in interactive mode. You will be prompted to provide website URL and some basic information.

You can also run it in console with arguments. Open command line (cmd, Powershell), navigate to directory with `page-walker` and run for example:
```
.\page-walker.exe -u http://example.com -p 5 --headless yes
```

On Windows, Chrome browser location is detected automatically.

#### Linux

Open terminal, navigate to directory with `page-walker` and run for example:
```
./page-walker -u http://example.com -p 5 --headless yes
```
On Linux, default Chrome browser is set to `google-chrome`. Maybe on your system is different and you need to provide this:
```
./page-walker -u http://example.com -p 5 --chrome-binary chromium-browser
```

### HTML reports

Reports (test results) are saved to `output` directory. For example: `output/2018-07-04_17-45-08_251870/report/index.html`. For your convince you will notice file `output/latest_report.html` redirecting to the latest report.

# Running from source code

Page Walker is a cross-platform Python application. You can run it on any system (Windows, Linux, Mac).

### Requirements

* Python 3 (Python 2 is not supported)
* Python modules
  * `requests`
  * `websocket-client`
* [v.Nu validator](https://github.com/validator/validator/releases)

If you have both Python 2 and 3 installed, you may need to use `pip3` and `python3` commands.

### Installation

* Install (and upgrade) Python modules
```
pip install --upgrade --user -r requirements.txt
```
* Download [v.Nu validator](https://github.com/validator/validator/releases) `vnu.jar_[version].zip` and unpack to `lib` directory (`lib/vnu/vnu.jar`)

### Running

Open console, navigate to project root directory and run (for example):
```
python pagewalker --url http://example.com --pages 5
```

# Features

This is not list of all features. See _Configurable parameters_ table for more information.

#### Interactive HTML reports

The result of `page-walker` run is [report like this](https://rafal-qa.com/pagewalker-example-report/). It's a stand-alone HTML/CSS/JavaScript page independent of Page Walker. You can browse it on local computer, send to someone, publish on your intranet. You can also easily integrate it with Jenkins (or other CI tools) - note `output/latest_report.html` file and `--keep-previous` option.

#### Headless mode

Running Chrome in headless mode keeps browser window invisible. You can run tests on remote command line out-of-the-box.

#### Validate HTML before/after JavaScript execution

Feature called _2-step HTML validation_
1. First step: Validate raw HTML, original page source received from server.
2. Second step: Validate HTML code exported from DOM after JavaScript execution. It saves errors that did not appear on first step. On most websites JavaScript modify page structure and now you can check if these changes are correct. You will also see that possible errors are related to JavaScript, because they did not occur on raw HTML.

For HTML validation [Nu Html Checker (v.Nu)](https://validator.github.io/validator/) is used. The same library as used by [W3C Markup Validator](https://validator.w3.org/).

#### Parallel test execution

Run multiple instances of same Chrome browser in parallel (or different versions if you wish). Just run multiple `page-walker` commands with different Chrome remote debugger port for every instance. If you run second instance with the same port number as already running, first instance will be stopped.

#### Scrolling page after load

This feature helps collect more data and detect more bugs. When page is loaded, scrolling to the bottom of page occurs. This action can fire more JavaScript events, AJAX requests, show more images. It you don't like this idea, you can disable it.

#### Custom list of pages

By default Page Walker is finding links to other pages within domain and visiting them. When you have specific list of pages to visit in specific order, you can use it. Save this list in text file, one page per line. Every page is relative to domain. For URL `http://example.com/login` domain is `http://example.com` and page is `/login`. Provide path to this file in argument `--pages-list`.

Pay attention to `--list-only` argument.
* If set to `yes`: only pages from list will be visited and no other pages. Option _maximum number of pages to visit_ has no effect.
* If set to `no`: option _maximum number of pages to visit_ is taken into account. After visiting pages from list, pages found automatically will be visited.

#### Login to restricted area

You can login in different ways:
1. Provide HTTP Basic authentication credentials
2. Fill in the login form using _Initial actions_
3. Add custom cookies with authentication data

#### Other features

* [Domain blacklist](docs/domain-blacklist.md) - simple malware detection
* [Custom cookies](docs/custom-cookies.md) - add cookies to browser before test starts
* [Initial actions](docs/initial-actions.md) - set text, click, submit before test starts

# Configuration

### Interactive mode

You can run Page Walker without any parameters. It's the same as double-clicking stand-alone executable on Windows. You will be asked to provide URL of website to test, number of pages to visit and whether to run in headless mode.

### 3-level configuration

1. Hard-coded defaults. Java and Chrome binary are dynamic and depends on operating system. On Windows location of installed Chrome is auto-detected.
2. Configuration file `config/main.ini`. It overwrites hard-coded defaults. If parameter is empty or omitted, hard-coded default will be used. Use it to configure your environment: custom location of Chrome, Java, parameters that you do not plan to change.
3. Command line arguments. It overwrites hard-coded defaults and configuration file parameters. Run with `-h` parameter to see all available options.

### Configurable parameters

| Command_line argument | `config/main.ini` | Default value | Description |
| --------------------- | ----------------- | ------------- | ----------- |
| `-u` or `--url` | `start_url` | | URL of first page to visit, with `http(s)://`. |
| `-p` or `--pages` | `max_number_pages` | 10 | Maximum number of pages to visit. |
| `-l` or `--headless` | `chrome_headless` | no | [yes/no] Run Chrome in headless mode. |
| `--pages-list` | `pages_list_file` | | [Optional] File containing list of pages to visit. Pages relative to main domain, starting with `/`. |
| `--list-only` | `pages_list_only` | yes | [yes/no] Visit all and only pages from file, regardless of _maximum number of pages_ value. Option has no effect if file with pages list is not set. |
| `--wait-after` | `wait_time_after_load` | 1 | Wait time (in seconds) after page was loaded (browser received `Load` event). Even after `Load` event the browser usually downloads some data so it's better to set it for 1-3 seconds.
| `--scroll-after` | `scroll_after_load` | yes | [yes/no] Scroll to bottom of page after page was loaded, before _wait time_. While scrolling browser can receive more events and data to analyze. |
| `--keep-previous` | `keep_previous_data` | yes | [yes/no] Keep data from previous program run. If _no_, `output` directory will be cleaned before run. |
| `--window-size` | `window_size` | 1366x768 | Size of browser window. |
| `--close-on-finish` | `chrome_close_on_finish` | yes | [yes/no] Close browser after finish. For debugging you can set to _no_ to interact with browser after app has finished running. |
| `--chrome-port` | `chrome_debugging_port` | 9222 | Chrome remote debugger port number. To run multiple tests in parallel set different port for every instance. |
| `--chrome-timeout` | `chrome_timeout` | 30 | Chrome connection timeout in seconds. How long to wait for `Load` event. |
| `--chrome-binary` | `chrome_binary` | Auto-detected on Windows, `google-chrome` otherwise. | Path to Chrome executable file. |
| `--chrome-ignore-cert` | `chrome_ignore_cert` | no | [yes/no] Ignore SSL errors. Set to _yes_ if you want to test a website with invalid SSL certificate. |
| `--http-auth` | `http_basic_auth_data` | | HTTP Basic authentication credentials in format `login:password` |
| `--cookies-file` | `custom_cookies_file` | | Config file with custom cookies definition, more: [Custom cookies](docs/custom-cookies.md) |
| `--initial-actions-file` | `initial_actions_file` | | Config file with initial actions definition, more: [Initial actions](docs/initial-actions.md) |
| `--initial-actions-url` | `initial_actions_url` | the same as `start_url` | URL of the page on which to perform initial actions. Option has no effect if `initial_actions_file` was not set. |
| `--validate` | `validator_enabled` | yes | [yes/no] Enable HTML validator. Set to _no_ if you don't have Java installed. |
| `--check-css` | `validator_check_css` | yes | [yes/no] Check also inline CSS. Option has no effect if HTML validator is disabled. |
| `--validator-warnings` | `validator_show_warnings` | yes | [yes/no] Report also warnings (in addition to errors). Option has no effect if HTML validator is disabled. |
| | `validator_vnu_jar` | `lib/vnu/vnu.jar` | Path to vNu HTML validator JAR file. |
| `--java-binary` | `java_binary` | `Java` on Windows, `java` otherwise. | Path to Java executable file. To use custom Java unpacked to `lib` directory, set for example to `lib/jre{ver}/bin/java` |
| | `java_stack_size` | 4096 | Java stack size [KB]. If you experience stack overflow errors while validating extremely large HTML page, increase it. |
| `--check-links` | `check_external_links` | yes | [yes/no] Check HTTP response status of external links. |
| | `check_external_links_timeout` | 10 | External links checking connection timeout in seconds. | 
| `--domain-blacklist` | `domain_blacklist_enabled` | yes | [yes/no] Check if domains are blacklisted due to malware, scam. |
| | `domain_blacklist_cache_expiry` | 24 | Domain blacklist cache expiry in hours. |
| | `domain_blacklist_auto_update` | yes | Domain blacklist auto update. |
| | `domain_blacklist_url` | [URL](https://raw.githubusercontent.com/rafal-qa/page-walker/master/lib/pagewalker/domain_lists.json) | URL with current domain lists. |
| `-v` or `--version` | | | Show app and Python version and exit. |
| `-h` or `--help` | | | Show all command line options. |

##### Boolean values

For boolean values (yes/no) you can also use:
* instead of `yes`: `y`, `true`, `1`
* instead of `no`: `n`, `false`, `0`

### Examples

Replace `page-walker` with:
* `.\page-walker.exe` when running Windows stand-alone version
* `./page-walker` when running Linux stand-alone version
* `python pagewalker` when running from source code

Visit max. 100 pages in headless mode
```
page-walker -u http://example.com/ -p 100 --headless yes
```

Visit all pages from list in file with no HTML validation
```
page-walker -u http://example.com/ --pages-list config/pages.txt --validate no
```

Run with custom Java (downloaded to `lib` directory) and Chrome (installed Beta version on Linux)
```
page-walker -u http://example.com/ --java-binary lib/jdk-10.0.1/bin/java --chrome-binary google-chrome-beta
```

Run 2 website tests in parallel (run commands in separate consoles)
```
page-walker -u http://example.com/ -p 100 --headless yes
page-walker -u http://example.org/ -p 100 --headless yes --chrome-port 9223
```

# Limitations and known problems

#### ERROR: Unable to connect to Chrome remote debugger (see log file for details)

Chrome logs are saved to `output/{date}_{time}/chrome_run.log`. Probably there is some Chrome issue, not related to Page Walker. For debugging purposes run Chrome from console. If `chrome_run.log` is empty, maybe you are trying to run Chrome in non-headless mode on remote server without GUI.

#### ERROR: Chrome not found at location: google-chrome

On Linux `google-chrome` is default Chrome location. Add custom name for example: `--chrome-binary chromium-browser`. It may be necessary to specify the full path.

#### [FAIL] Network.getResponseBody | No resource with given identifier found

This error does not stop program, only appears in the console. It occurs when Chrome lost information about some response received previously. Usually caused by non HTTP redirection to other page.

#### net::ERR_ABORTED

You can see this error in HTML report. Sometimes lots of them. When using DevTools manually it's equivalent to `(canceled)` error in _Network_ tab. The reasons may be different, and sometimes difficult to reproduce. [Read this great topic on StackOverflow](https://stackoverflow.com/questions/12009423/what-does-status-canceled-for-a-resource-mean-in-chrome-developer-tools). This can be related to some page issues, so it's worth analyzing.

# More information

* [Domain blacklist](docs/domain-blacklist.md)
* [Custom cookies](docs/custom-cookies.md)
* [Initial actions](docs/initial-actions.md)
* [How it works](docs/how-it-works.md)
* [Changelog](CHANGELOG.md)

## TODO

What improvements you can expect in future releases.
* Developer guide, more technical details.
* Skipped errors, known errors you won't fix. Manually created list of errors that will not be reported.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments

HTML report uses following libraries included in `lib/pagewalker/report_template/lib/`:
* [Semantic UI](https://github.com/Semantic-Org/Semantic-UI-CSS) licensed under the MIT License, Copyright (c) 2015 Semantic Org
* [jQuery](https://jquery.com) licensed under the MIT License, Copyright JS Foundation and other contributors
* [DataTables](https://datatables.net) licensed under the MIT License, Copyright (C) 2008-2018, SpryMedia Ltd.

[Nu Html Checker (v.Nu)](https://github.com/validator/validator) is licensed under the MIT License, Copyright (c) 2007-2016 Mozilla Foundation
