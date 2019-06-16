# Page Walker

*Zero-configuration test automation tool.*

Chrome DevTools automation for desktop and mobile devices.

The result is an interactive report - [see example report](https://rafal-qa.com/pagewalker-example-report/).

### How it can help in testing?

* Automatically collects and analyzes data from Chrome DevTools for multiple subpages
  * Finds network errors, failed requests while loading page
  * Finds JavaScript runtime exceptions
  * Collects DevTools Console errors and other logs
* Testing mobile website
  * Mobile browser emulator
  * Chrome for Android on physical device
* Finds broken links (internal and external)
* Looking for blacklisted domains (malware detection)
  * Requests to these domains while loading page
  * Links to these domains
* Validates HTML, CSS - before and after JavaScript execution
* Logs in to restricted area

### Links

* [Project homepage](https://rafal-qa.com/page-walker/)
* [Source code](https://github.com/rafal-qa/page-walker)
* [Latest standalone release](https://github.com/rafal-qa/page-walker/releases/latest)

# Table of contents

* [Getting started](#getting-started)
* [Running from source code](docs/running-from-source.md)
* [Features](docs/features.md)
* [Configuration](docs/configuration.md)
* How to configure
  * [Chrome on Android device](docs/chrome-for-android.md)
  * [Custom cookies](docs/custom-cookies.md)
  * [Initial actions](docs/initial-actions.md)
* [Known problems](docs/known-problems.md)
* [Changelog](CHANGELOG.md)
* [License](#license)
* [Acknowledgments](#acknowledgments)

# Getting started

1. **[Download](https://github.com/rafal-qa/page-walker/releases/latest) latest standalone release** - it contains required dependencies, no installation or configuration is needed
2. Unpack `zip` file (the same file for Windows, macOS, Linux)
3. Make sure, current Google Chrome (or Chromium) browser is installed (at least version 66).

Reports (test results) are saved to `output` directory.

### Windows

Standalone release contains Python embeddable for Windows, so you don't need Python installed.

Double-click `pagewalker` (Batch File) and it will run in the interactive mode. You will be prompted to provide website URL and some basic information.

You can also run it in command line with arguments. Open `cmd` or `PowerShell` and navigate to `page-walker` root directory (i.e. containing `README` file).

Display available options:
```
.\pagewalker -h
```

Run test for 5 pages in headless mode:
```
.\pagewalker -u http://example.com -p 5 --headless yes
```

### Linux & macOS

You will need Python 3 installed on your system.

* On **Linux** - you probably already have it installed
* On **macOS** - you can install it with `Homebrew` package manager, see instruction in the article [Install Python 3 on Mac](https://wsvincent.com/install-python3-mac/)

Open terminal and navigate to `page-walker` root directory (i.e. containing `pagewalker.sh` file).

Display available options:
```
./pagewalker.sh -h
```

Run test for 5 pages in headless mode:
```
./pagewalker.sh -u http://example.com -p 5 --headless yes
```

### Optional steps

#### Install Java

For using HTML/CSS validator Java 8 (or newer) is required, but you can disable this feature.

* **Windows** - You can download Java installer from [AdoptOpenJDK website](https://adoptopenjdk.net)
* **macOS** - You can install it with `Homebrew` package manager with command: `brew cask install java`

#### Configure testing on Android device

See: [Chrome on Android device](docs/chrome-for-android.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments

HTML report uses following libraries included in `pagewalker/resources/report_template/lib/`:
* [Semantic UI](https://github.com/Semantic-Org/Semantic-UI-CSS) licensed under the MIT License, Copyright (c) 2015 Semantic Org
* [jQuery](https://jquery.com) licensed under the MIT License, Copyright JS Foundation and other contributors
* [DataTables](https://datatables.net) licensed under the MIT License, Copyright (C) 2008-2018, SpryMedia Ltd.

[Nu Html Checker (v.Nu)](https://github.com/validator/validator) is licensed under the MIT License, Copyright (c) 2007-2016 Mozilla Foundation
