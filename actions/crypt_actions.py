import os
import shutil
from action import Action
import utils
from file_crypt import FileCrypt


class CryptFilesAction(Action):
    def run(self, args):
        config = self.config

        from_dir = self.translate_string(config["from"])
        if not os.path.isabs(from_dir):
            from_dir = os.path.join(self.runner.project_root_path, from_dir)

        if "to" in config:
            to_dir = self.translate_string(config["to"])
            if not os.path.isabs(to_dir):
                to_dir = os.path.join(self.runner.project_root_path, to_dir)
        else:
            to_dir = from_dir

        if "key" in config:
            key = self.translate_string(config["key"]).encode("utf8")
        else:
            key = None

        if "sign" in config:
            sign = self.translate_string(config["sign"]).encode("utf8")
        else:
            sign = None

        include = None
        if "include" in config:
            include = config["include"]

        exclude = None
        if "exclude" in config:
            exclude = config["exclude"]

        rule = utils.create_rules(include, exclude)

        remove_source = True
        if "remove_source" in config:
            remove_source = config["remove_source"]

        fcrypt = FileCrypt(key, sign, rule)
        fcrypt.start_encrypt(from_dir, to_dir, remove_source)
