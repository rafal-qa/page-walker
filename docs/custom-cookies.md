# Custom cookies

Thanks to this option, you can add your own cookies to the browser. Use it to add session info, disable annoying popup, etc.

## Configuration

To enable this feature, create configuration `.ini` file and provide location to it:
```
--cookies-file config/custom_cookies.ini
```

Example file with comments: [config/examples/custom_cookies.ini](../config/examples/custom_cookies.ini)

Minimal configuration of single cookie:
```
[your_informative_cookie_name]
name = cookie_name
value = cookie_value
```

Other optional values:
```
domain = example.com
path = /admin
secure = true
httponly = true
```

### Why no "expires" option?

Because all previous data including cookies are deleted before new test. So all cookies are session cookies. This option could create confusion.
