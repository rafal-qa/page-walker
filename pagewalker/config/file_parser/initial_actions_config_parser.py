from .ini_reader import INIReader
from pagewalker.utilities import error_utils
from pagewalker.config import config


class InitialActionsConfigParser(INIReader):
    REQUIRED_OPTIONS = {
        "set_text": ["text", "css"],
        "click": ["css"],
        "submit": ["css"],
        "wait_element_present": ["timeout", "css"]
    }

    def __init__(self):
        super(InitialActionsConfigParser, self).__init__(config.initial_actions_file)

    def apply(self):
        actions_data = []
        for section in self._get_sections():
            actions_data.append(self._single_action(section))
        if actions_data:
            config.initial_actions_data = actions_data

    def _single_action(self, section):
        action_data = self._get_non_empty_values(section)
        if "action" not in action_data:
            self._error_missing_option("action", section)
        self._validate_known_actions(action_data["action"])
        self._validate_required_options(action_data, section)
        action_data["step"] = section
        return action_data

    def _validate_known_actions(self, action):
        if action not in self.REQUIRED_OPTIONS:
            msg = "Unknown action '%s' in initial actions file '%s'" % (action, config.initial_actions_file)
            error_utils.exit_with_message(msg)

    def _validate_required_options(self, action_data, section):
        action = action_data["action"]
        for option in self.REQUIRED_OPTIONS[action]:
            if option not in action_data:
                self._error_missing_option(option, section)

    def _error_missing_option(self, option, section):
        msg = "Missing '%s' in step [%s] in initial actions file '%s'" \
              % (option, section, config.initial_actions_file)
        error_utils.exit_with_message(msg)
