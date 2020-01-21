### Download Chrome browser binary in any version

Script returns direct link to download standalone/portable Chrome (Chromium) binary - for use without installation. It finds the newest build for given major version and given OS.

Note that not every build for every OS is available to download from
[Chromium browser snapshots page](https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html). Windows can be problematic.

#### Examples

Latest version for macOS:

```bash
python download-chrome-binary.py --system mac
```

Version 79 for Linux:

```bash
python download-chrome-binary.py --system linux64 --version 79
```

Available systems: `win32, win64, linux64, mac`
