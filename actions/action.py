import os


class Action:
    def __init__(self, runner, config):
        self.runner = runner
        self.config = config

        self._parse_config()

    def _parse_config(self):
        print("should parse in sub class")

    def translate_string(self, s):
        return self.runner.translate_string(s)

    def get_full_path_from_config(self, key, root_path):
        if key not in self.config:
            return None

        file_path = self.translate_string(self.config[key])
        if not os.path.isabs(file_path):
            file_path = os.path.join(root_path, file_path)
        return file_path

    def run(self, args):
        print("should run in sub class")
