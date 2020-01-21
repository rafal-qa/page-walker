### Download Chrome browser binary in any version

Script returns direct link to download standalone/portable Chrome (Chromium) binary. It finds the newest build for given major version and given OS.

Note that not every build for every OS is available for download from
https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html

#### Examples

Latest version for Windows 64-bit:

```bash
python download-chrome-binary.py --system win62
```

Version 79 for macOS:

```bash
python download-chrome-binary.py --system mac --version 79
```

Available systems: `win32, win64, linux64, mac`
