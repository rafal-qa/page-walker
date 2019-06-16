# Known problems

#### ERROR: Unable to connect to Chrome remote debugger (see log file for details)

Chrome logs are saved to `output/{date}_{time}/chrome_run.log`. Probably there is some Chrome issue, not related to Page Walker. For debugging purposes run Chrome from console. If `chrome_run.log` is empty, maybe you are trying to run Chrome in non-headless mode on remote server without GUI.

#### ERROR: Chrome not found at location: google-chrome

On Linux `google-chrome` is default Chrome location. Add custom name for example: `--chrome-binary chromium-browser`. It may be necessary to specify the full path.

#### [FAIL] Network.getResponseBody | No resource with given identifier found

This error does not stop program, only appears in the console. It occurs when Chrome lost information about some response received previously. Usually caused by non HTTP redirection to other page.

#### net::ERR_ABORTED

You can see this error in HTML report. Sometimes lots of them. When using DevTools manually it's equivalent to `(canceled)` error in _Network_ tab. The reasons may be different, and sometimes difficult to reproduce. [Read this great topic on StackOverflow](https://stackoverflow.com/questions/12009423/what-does-status-canceled-for-a-resource-mean-in-chrome-developer-tools). This can be related to some page issues, so it's worth analyzing.