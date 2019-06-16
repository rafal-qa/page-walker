# Running from source code

Page Walker is a cross-platform Python application. You can run it on any system (Windows, macOS, Linux).

### Requirements

* Python 3 (Python 2 is not supported)
* Python modules
  * `requests`
  * `websocket-client`
* [v.Nu validator](https://github.com/validator/validator/releases)
* Java 8 (or newer)

If you have both Python 2 and 3 installed, you may need to use `pip3` and `python3` in the following commands.

### Installation

* Install (and upgrade) Python modules
```
pip install --upgrade --user -r requirements.txt
```
* Download [v.Nu validator](https://github.com/validator/validator/releases) `vnu.jar_[version].zip` and unpack to `lib` directory, file structure: `lib/vnu/vnu.jar`

### Running

Open terminal and navigate to `page-walker` root directory.

Display available options:
```
python pagewalker -h
```

Run test for 5 pages in headless mode:
```
python pagewalker -u http://example.com -p 5 --headless yes
```