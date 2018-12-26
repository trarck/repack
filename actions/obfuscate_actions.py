import os
import random
from action import Action
import utils
from resource.resource_obfuscator import ResourceObfuscator
from resource.resource_mapping import ResourceMapping


class ObfuscateResourcesAction(Action):
    def run(self, args):
        config = self.config

        crypt_info = self.runner.crypt_info.copy()
        res_path = config["res_path"]
        if not os.path.isabs(res_path):
            res_path = os.path.join(self.runner.project_root_path, res_path)

        sub_dirs = None
        if "sub_dirs" in config:
            sub_dirs = config["sub_dirs"]

        ignore_dirs = None
        if "ignore_dirs" in config:
            ignore_dirs = config["ignore_dirs"]

        remove_source = True
        if "remove_source" in config:
            remove_source = config["remove_source"]

        if "out_path" in config:
            out_path = config["out_path"]
            if not os.path.isabs(out_path):
                out_path = os.path.join(self.runner.project_root_path, out_path)
        else:
            out_path = res_path

        if "with_ext" in config:
            crypt_info.with_ext = config["with_ext"]

        include_rules = None
        if "include_rules" in config:
            include_rules = utils.convert_rules(config["include_rules"])

        exclude_rules = None
        if "exclude_rules" in config:
            exclude_rules = utils.convert_rules(config["exclude_rules"])

        res_obf = ResourceObfuscator(res_path, out_path, sub_dirs, ignore_dirs, crypt_info, include_rules,
                                     exclude_rules, remove_source)
        res_obf.start()


class MappingResourcesAction(Action):
    def run(self, args):
        config = self.config

        crypt_info = self.crypt_info.copy()
        res_path = self.translate_string(config["res_path"])
        if not os.path.isabs(res_path):
            res_path = os.path.join(self.runner.project_root_path, res_path)

        if "out_path" in config:
            out_path = self.translate_string(config["out_path"])
            if not os.path.isabs(out_path):
                out_path = os.path.join(self.runner.project_root_path, out_path)
        else:
            out_path = res_path

        mapping_file = None
        if "mapping_file" in config:
            mapping_file = self.translate_string(config["mapping_file"])
            if not os.path.isabs(out_path):
                out_path = os.path.join(self.runner.project_root_path, out_path)

        remove_source = True
        if "remove_source" in config:
            remove_source = config["remove_source"]

        if "with_ext" in config:
            crypt_info.with_ext = config["with_ext"]

        ignore_root = True
        if "ignore_root" in config:
            ignore_root = config["ignore_root"]

        save_json = False
        if "save_json" in config:
            save_json = config["save_json"]

        save_plist = False
        if "save_plist" in config:
            save_plist = config["save_plist"]

        include_rules = None
        if "include_rules" in config:
            include_rules = config["include_rules"]

        exclude_rules = None
        if "exclude_rules" in config:
            exclude_rules = config["exclude_rules"]

        rule = utils.create_rules(include_rules, exclude_rules)

        min_level = 2
        if "min_level" in config:
            min_level = config["min_level"]

        max_level = 5
        if "max_level" in config:
            max_level = config["max_level"]

        level = random.randint(min_level, max_level)

        min_dir_counts = [10, 6]
        if "min_dir_counts" in config:
            min_dir_counts = config["min_dir_counts"]

        max_dir_counts = [15, 10]
        if "max_dir_counts" in config:
            max_dir_counts = config["max_dir_counts"]

        res_mapping = ResourceMapping(res_path, rule, remove_source, crypt_info.with_ext)
        res_mapping.mapping(level, min_dir_counts, max_dir_counts, out_path, ignore_root)
        res_mapping.save_mapping_data(mapping_file, crypt_info.key, save_json, save_plist)
