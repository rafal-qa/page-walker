# Features

This is not list of all features. See [Configuration](configuration.md) for complete information.

### Interactive HTML reports

The result of `pagewalker` run is [report like this](https://rafal-qa.com/pagewalker-example-report/). It's a standalone HTML/CSS/JavaScript page independent of Page Walker. You can browse it on local computer, send to someone, publish on your intranet. You can also easily integrate it with Jenkins (or other CI tools).

### Testing mobile website

By default Chrome desktop is used for website browsing.

For testing mobile version of your website you have 2 options:
* Use DevTools mobile browser emulation with no additional configuration, add command line parameter: `--mobile-emulation yes`
* Run Chrome on physical device, see: [Chrome on Android device](chrome-for-android.md)

### Headless mode

Running Chrome in headless mode keeps browser window invisible. You can run tests on remote server with no GUI out-of-the-box.

### Validate HTML before/after JavaScript execution

Feature called _2-step HTML validation_
1. First step: Validate raw HTML, original page source received from server.
2. Second step: Validate HTML code exported from DOM after JavaScript execution. It saves errors that did not appear on first step. On most websites JavaScript modify page structure and now you can check if these changes are correct. You will also see that possible errors are related to JavaScript, because they did not occur on raw HTML.

For HTML validation [Nu Html Checker (v.Nu)](https://validator.github.io/validator/) is used. The same library as used by [W3C Markup Validator](https://validator.w3.org/).

### Parallel test execution

Run multiple instances of same Chrome browser in parallel (or different versions if you wish). Just run multiple `pagewalker` commands with different Chrome remote debugger port for every instance. If you run second instance with the same port number as already running, first instance will be stopped.

### Scrolling page after load

This feature helps collect more data and detect more bugs. When page is loaded, scrolling to the bottom of page occurs. This action can fire more JavaScript events, AJAX requests, show more images. It you don't like this idea, you can disable it.

### Custom list of pages

By default Page Walker is finding links to other pages within domain and visiting them. When you have specific list of pages to visit in specific order, you can use it. Save this list in text file, one page per line. Every page is relative to domain. For URL `http://example.com/login` domain is `http://example.com` and page is `/login`. Provide path to this file in argument `--pages-list`.

Pay attention to `--list-only` argument.
* If set to `yes`: only pages from list will be visited and no other pages. Option _maximum number of pages to visit_ has no effect.
* If set to `no`: option _maximum number of pages to visit_ is taken into account. After visiting pages from list, pages found automatically will be visited.

### Login to restricted area

You can login in different ways:
1. Provide HTTP Basic authentication credentials
2. Fill in the login form using [Initial actions](initial-actions.md)
3. Add [Custom cookies](custom-cookies.md) with authentication tokens

### Simple malware detection

See: [Domain blacklist](domain-blacklist.md)
