# Changelog

## v1.2.0 (2019-06-16)

#### New features

* Mobile website testing - mobile emulation, Chrome on Android device

#### Improvements

* Check external links in multiple threads
* Improved macOS support
* New way of handling standalone version

#### Other

* Stop supporting Python 2
* Removed unnecessary configuration

## v1.1.0 (2018-12-02)

#### New features

* Broken external links detection.
* Custom cookies.
* Initial actions - set text, click, submit before test starts.
* HTTP Basic authentication.
* Domain blacklist (malware domains).

#### Improvements

* Run program from any location.
* Now checking HTTP headers with GET request (without downloading body), not HEAD (some servers don't support it or block).
* `google-chrome` is now default browser on Linux.
* Other minor improvements.

#### Bugfixes

* Handling URLs with no scheme: `//example.com`
* Duplicated home page links: `example.com/` and `example.com`

## v1.0.1 (2018-10-23)

#### Improvements

* HTML report: Information about backlink on _Pages list_ was added.
* HTML report: More understandable names of tabs on _HTML validator_.
* Now the program is not terminated when it detects lack of Java. It shows only the warning message and disables the HTML validator. The user does not have to search for the option to disable the validator manually.
* Other minor improvements.

#### Bugfixes

* Incorrect data in the report when the subpage redirects to the external domain. Now pages with redirect or error HTTP code (like `404 Not Found`) are not visited by Chrome DevTools. Only information about redirection or error is reported.
* HTML report: Tables was not resized on window resize.
* Other minor fixes.

## v1.0.0 (2018-07-08)

First public release.
