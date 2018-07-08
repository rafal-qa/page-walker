# How it works

Page Walker runs Chrome browser in remote debugging mode and communicate with Chrome using [DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/). Information is exchanged by Web Socket connection only. No other libraries (like Selenium WebDriver) is needed. While crawling a website data form DevTools is saved to SQLite database. When crawling is done, HTML report is generated from collected data.

**[TODO] More technical details soon.**