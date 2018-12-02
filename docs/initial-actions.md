# Initial actions

Custom actions before test starts: set input text, click element, submit from, wait for element. Like Selenium but much more simple and limited. Use it to fill in the login form.

## Configuration

To enable this feature, create configuration `.ini` file and provide location to it:
```
--initial-actions-file config/initial_actions.ini
```

Example file with comments: [config/examples/initial_actions.ini](../config/examples/initial_actions.ini)

Configuration of single action:
```
[your_informative_action_name]
action = action_name
text = example text
css = .class_name
```

| `action` name | Required additional options | Description |
| ------------- | ---------------- | ----------- |
| `set_text` | `css`, `text` | Set `text` to element located by `css`. |
| `click` | `css` | Click element located by `css`. |
| `submit` | `css` | Submit form located by `css`. |
| `wait_element_present` | `css`, `timeout` | Wait max. `timeout` seconds until element located by `css` is present. |

### Initial actions URL

By default browser loads `start_url`, performs initial actions and opens `start_url` as usual.

To perform actions on different URL, use `--initial-actions-url` option. For example:
```
--url example.com/admin_area
--initial-actions-url example.com/login_page
```
