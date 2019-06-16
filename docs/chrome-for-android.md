# Chrome for Android

For using Google Chrome on Android device you need to take a few steps.

### Step 1: Configure connection between your computer and Android device

Chrome desktop browser has built-in support for remote debugging Android device. Configure it following official documentation: [Get Started with Remote Debugging Android Devices](https://developers.google.com/web/tools/chrome-devtools/remote-debugging/)

Make sure it runs as expected.

### Step 2: Configure and run Page Walker

Page Walker uses *Android Debug Bridge* (adb) to provide remote debugging connection to Android device. ADB is a part of *SDK Platform Tools*.

[Download Platform Tools](https://developer.android.com/studio/releases/platform-tools.html) for your system and unpack to `lib` directory in `page-walker` root directory. Default ADB location in Page Walker is `lib/platform-tools/adb` (file `adb` in `platform-tools` directory).

Run Page Walker with command line option: `--android-browser yes`

## How it works

#### Clearing the cache

When running Chrome desktop (or mobile emulation) temporary profile directory is always deleted. This profile contains all data: cache, cookies, history.

With Chrome for Android it's not possible. Instead of, before each test:
* Browser cache is cleared (but no cookies, history)
* Previous cookies only for tested website are deleted

#### No resource with given identifier found

```
[FAIL] Network.getResponseBody | No resource with given identifier found
```

Above message can mean:
* Your device has no internet connection.
* Chrome browser on device is not running. Try to open Chrome. Normally it's enough to run in the background.
