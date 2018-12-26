class Action:
    def __init__(self, runner, config):
        self.runner = runner
        self.config = config

    def parse_config(self):
        print("should parse in sub class")

    def run(self, args):
        print("should run in sub class")
