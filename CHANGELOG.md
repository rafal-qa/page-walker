# Changelog

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
