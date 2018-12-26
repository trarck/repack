# -*- coding: utf-8 -*-
import os
import sys
import traceback
import shutil
import random
import json
from string import Template

from argparse import ArgumentParser
from resource.resource_obfuscator import ResourceObfuscator, CryptInfo
from project import IosProject
from source_file import SourceFile
from file_crypt import FileCrypt
from garbage_code.cpp_garbage_code import CppGarbageCode
from resource.resource_garbage import ResourceGarbage
from garbage_code.objc_garbage_code import ObjCGarbageCode
from garbage_code.cpp_injector import CppInjector
from resource.resource_mapping import ResourceMapping

import utils

reload(sys)
sys.setdefaultencoding('utf-8')


class Repack:
    def __init__(self, matrix_project_root_path, project_root_path, pack_resource_path, global_data_dir, name):
        self.matrix_project_root_path = matrix_project_root_path
        self.project_root_path = project_root_path
        self.pack_resource_path = pack_resource_path
        self.global_data_dir = global_data_dir
        self.name = name
        self.crypt_info = CryptInfo(None, "md5")
        self.need_copy_project = False

        self._config_data = None

        self._environment = {
            u"MATRIX_PROJECT_ROOT": self.matrix_project_root_path,
            u"PROJECT_ROOT": self.project_root_path,
            u"PACK_RESOURCE_ROOT": self.pack_resource_path,
            u"GLOBAL_DATA_DIR": self.global_data_dir
        }

        self.action_classes = {}

    def _merge_environment(self, conf_data, parent_key=None):
        for key, value in conf_data.items():
            if parent_key:
                new_key = parent_key + '_' + key.upper()
            else:
                new_key = key.upper()

            if isinstance(value, (dict)):
                self._merge_environment(value, new_key)
            elif isinstance(value, (list)):
                print("ignore list for %s" % key)
            else:
                self._environment[new_key] = value

    def translate_string(self, value):
        t = Template(value)
        return t.substitute(self._environment)

    def parse_config(self, conf_data):
        self._config_data = conf_data

        if "need_copy" in conf_data:
            self.need_copy_project = conf_data["need_copy"]

        if not self.project_root_path:
            if self.need_copy_project:
                self.project_root_path = os.path.join(os.path.dirname(self.matrix_project_root_path), self.name)
            else:
                self.project_root_path = self.matrix_project_root_path

        if "name" in conf_data:
            self.name = conf_data["name"]

        if "crypt" in conf_data:
            self.crypt_info.parse_config(conf_data["crypt"])

        if not self.crypt_info.key:
            self.crypt_info.key = utils.generate_key()

        if "xcode_project_name" not in conf_data:
            conf_data["xcode_project_name"] = conf_data["target_name"] + ".xcodeproj"

        self._merge_environment(conf_data, "PROJECT")

    def register_actions(self, action_config_file):

        fp = open(action_config_file)
        action_data = json.load(fp)
        fp.close()

        if "actions" in action_data:
            for action_config in action_data["actions"]:
                cls = utils.get_class(action_config["class_name"])
                if cls:
                    self.action_classes[action_config["name"]] = cls

    def run(self,steps):
        if self.need_copy_project:
            self.copy_project()

        self.do_steps(steps)

    def do_steps(self, steps):
        for step_data in steps:
            self.do_step(step_data)

    def do_step(self, step_data):
        print("===> do step %s" % step_data["name"])
        if "actions" in step_data:
            self.do_actions(step_data["actions"])

    def do_actions(self, actions):
        for action_data in actions:
            self.do_action(action_data)

    def do_action(self, action_data):
        print("===> do action %s" % action_data["name"])
        if action_data["name"] in self.action_classes:
            action = self.action_classes[action_data["name"]](self, action_data)
            action.run(None)
        else:
            raise "Can't find action %s" % action_data["name"]

    def copy_project(self, config=None):
        print("copy project from %s to %s" % (self.matrix_project_root_path, self.project_root_path))
        if os.path.exists(self.matrix_project_root_path):
            if os.path.exists(self.project_root_path):
                shutil.rmtree(self.project_root_path)
            shutil.copytree(self.matrix_project_root_path, self.project_root_path, True)
        else:
            print("copy project error no %s folder " % self.matrix_project_root_path)

    def copy_files(self, config):
        print("===>copy file from %s to %s" % (
            self.translate_string(config["from"]), self.translate_string(config["to"])))

        src_dir = self.translate_string(config["from"])
        dst_dir = self.translate_string(config["to"])

        if not os.path.isabs(src_dir):
            src_dir = os.path.join(self.pack_resource_path, src_dir)

        if not os.path.isabs(dst_dir):
            dst_dir = os.path.join(self.project_root_path, dst_dir)

        utils.copy_files_with_config(config, src_dir, dst_dir)

    def delete_files(self, config):
        print("===>delete files ")
        for file_path in config["files"]:
            file_path = self.translate_string(file_path)
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.project_root_path, file_path)

            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            elif os.path.isfile(file_path):
                os.remove(file_path)

    def modify_files(self, config):
        if "files" in config:
            for modify_config in config["files"]:
                file_path = self.translate_string(modify_config["file_path"])
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.project_root_path, file_path)
                source = SourceFile(file_path)
                source.open()
                operation = modify_config["operation"]

                words = None
                if "words" in modify_config:
                    words = modify_config["words"]
                    words = self.translate_string(words)

                if "words_file" in modify_config:
                    words_file_path = self.translate_string(modify_config["words_file"])
                    if not os.path.isabs(words_file_path):
                        words_file_path = os.path.join(self.pack_resource_path, words_file_path)
                    fp = open(words_file_path)
                    words = fp.read()
                    fp.close()
                    words = self.translate_string(words)

                if operation == "insert":
                    source.insert(modify_config["keys"], words)
                elif operation == "insert_before":
                    source.insert_before(modify_config["keys"], words)
                elif operation == "replace":
                    olds = modify_config["olds"]
                    for i in range(len(olds)):
                        olds[i] = self.translate_string(olds[i])

                    news = modify_config["news"]
                    for i in range(len(news)):
                        news[i] = self.translate_string(news[i])

                    source.replace(olds, news)
                elif operation == "search_replace":
                    source.search_replace(modify_config["froms"], modify_config["tos"], words)
                elif operation == "search_replace_to_end":
                    source.search_replace_to_end(modify_config["froms"], modify_config["tos"], words)
                elif operation == "remove":
                    source.remove(modify_config["froms"], modify_config["tos"])
                source.save()

    def set_xcode_project(self, config):
        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        package_id = self.translate_string(config["package_id"])

        if "target_name" in config:
            target_name = self.translate_string(config["target_name"])

        else:
            target_name = self.name

        if "display_name" in config:
            display_name = self.translate_string(config["display_name"])
        else:
            display_name = target_name

        xcode_project_name = None
        if "xcode_project_name" in config:
            xcode_project_name = self.translate_string(config["xcode_project_name"])

        product_name = None
        if "product_name" in config:
            product_name = self.translate_string(config["product_name"])

        code_sign_identity = self.translate_string(config["code_sign_identity"])
        provisioning_profile = self.translate_string(config["provisioning_profile"])

        development_team = None
        if "development_team" in config:
            development_team = self.translate_string(config["development_team"])

        provisioning_profile_uuid = None
        if "provisioning_profile_uuid" in config:
            provisioning_profile_uuid = self.translate_string(config["provisioning_profile_uuid"])

        code_sign_entitlements = None
        if "code_sign_entitlements" in config:
            code_sign_entitlements = self.translate_string(config["code_sign_entitlements"])

        ios_project = IosProject(xcode_project_path)
        ios_project.rename(target_name, package_id, display_name, xcode_project_name, product_name)
        # ios_project.set_resource_obfuscate_key(self.crypt_info.key)
        ios_project.set_code_sign(code_sign_identity, provisioning_profile, development_team, provisioning_profile_uuid,
                                  code_sign_entitlements)

    def xcode_add_file(self, config):
        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        file_path = self.translate_string(config["file_path"])

        parent = None
        if "parent" in config:
            parent = self.translate_string(config["parent"])

        ios_project = IosProject(xcode_project_path)
        ios_project.add_file(file_path, parent)

    def build_xcode_app(self, config):
        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        target = self.translate_string(config["target"])
        configuration = self.translate_string(config["configuration"])
        sdk = self.translate_string(config["sdk"])
        out_put = self.translate_string(config["out_put"])

        ios_project = IosProject(xcode_project_path)
        ios_project.build_app(target, configuration, sdk, out_put)

    def build_xcode_archive(self, config):
        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        scheme = self.translate_string(config["scheme"])
        configuration = self.translate_string(config["configuration"])
        out_put = self.translate_string(config["out_put"])

        ios_project = IosProject(xcode_project_path)
        ios_project.build_archive(scheme, configuration, out_put)

    def crypt_files(self, config):
        from_dir = self.translate_string(config["from"])
        if not os.path.isabs(from_dir):
            from_dir = os.path.join(self.project_root_path, from_dir)

        if "to" in config:
            to_dir = self.translate_string(config["to"])
            if not os.path.isabs(to_dir):
                to_dir = os.path.join(self.project_root_path, to_dir)
        else:
            to_dir = from_dir

        if "key" in config:
            key = self.translate_string(config["key"]).encode("utf8")
        else:
            key = self._config_data["xxtea_key"]

        if "sign" in config:
            sign = self.translate_string(config["sign"]).encode("utf8")
        else:
            sign = self._config_data["xxtea_sign"]

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

    def obfuscate_resources(self, config):
        crypt_info = self.crypt_info.copy()
        res_path = config["res_path"]
        if not os.path.isabs(res_path):
            res_path = os.path.join(self.project_root_path, res_path)

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
                out_path = os.path.join(self.project_root_path, out_path)
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

    def mapping_resources(self, config):
        crypt_info = self.crypt_info.copy()
        res_path = self.translate_string(config["res_path"])
        if not os.path.isabs(res_path):
            res_path = os.path.join(self.project_root_path, res_path)

        if "out_path" in config:
            out_path = self.translate_string(config["out_path"])
            if not os.path.isabs(out_path):
                out_path = os.path.join(self.project_root_path, out_path)
        else:
            out_path = res_path

        mapping_file = None
        if "mapping_file" in config:
            mapping_file = self.translate_string(config["mapping_file"])
            if not os.path.isabs(out_path):
                out_path = os.path.join(self.project_root_path, out_path)

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

    def generate_code(self, config):
        out_folder_path = self.translate_string(config["out_dir"])
        if not os.path.isabs(out_folder_path):
            out_folder_path = os.path.join(self.project_root_path, out_folder_path)

        tpl_folder_path = self.translate_string(config["tpl_dir"])
        if not os.path.isabs(tpl_folder_path):
            tpl_folder_path = os.path.join(self.global_data_dir, tpl_folder_path)
        tpl_folder_path = tpl_folder_path.encode("utf-8")

        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        exec_code_file_path = self.translate_string(config["exec_code_file_path"])
        if not os.path.isabs(exec_code_file_path):
            exec_code_file_path = os.path.join(self.project_root_path, exec_code_file_path)

        cpp_code = CppGarbageCode(tpl_folder_path)
        action = cpp_code.generate_cpp_file(out_folder_path, xcode_project_path, exec_code_file_path, config)
        self.do_action(action)

    def inject_code(self, config):
        files = config["files"]
        del config["files"]
        checked_files = []
        for file_path in files:
            file_path = self.translate_string(file_path)
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.project_root_path, file_path)
            checked_files.append(file_path)

        tpl_folder_path = self.translate_string(config["tpl_dir"])
        if not os.path.isabs(tpl_folder_path):
            tpl_folder_path = os.path.join(self.global_data_dir, tpl_folder_path)

        tpl_folder_path = tpl_folder_path.encode("utf-8")

        config["tpl_folder"] = tpl_folder_path

        cpp_injector = CppInjector(config)
        cpp_injector.inject_files(checked_files)

    def generate_files(self, config):
        out_folder_path = self.translate_string(config["out_dir"])
        if not os.path.isabs(out_folder_path):
            out_folder_path = os.path.join(self.project_root_path, out_folder_path)

        rg = ResourceGarbage(out_folder_path, config)
        rg.generate_files()

    def generate_objc_class(self, config):
        out_folder_path = self.translate_string(config["out_dir"])
        if not os.path.isabs(out_folder_path):
            out_folder_path = os.path.join(self.project_root_path, out_folder_path)

        tpl_folder_path = self.translate_string(config["tpl_dir"])
        if not os.path.isabs(tpl_folder_path):
            tpl_folder_path = os.path.join(self.global_data_dir, tpl_folder_path)
        tpl_folder_path = tpl_folder_path.encode("utf-8")

        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        exec_code_file_path = self.translate_string(config["exec_code_file_path"])
        if not os.path.isabs(exec_code_file_path):
            exec_code_file_path = os.path.join(self.project_root_path, exec_code_file_path)

        objc_code = ObjCGarbageCode(tpl_folder_path)
        action = objc_code.generate_cpp_file(out_folder_path, xcode_project_path, exec_code_file_path, config)
        self.do_action(action)


def repack_project(src_project, out_dir, resource_dir, data_dir, project_config, step_config):
    if "project_path" in project_config:
        if os.path.isabs(project_config["project_path"]):
            project_path = project_config["project_path"]
        else:
            project_path = os.path.join(out_dir, project_config["project_path"])
    else:
        project_path = os.path.join(out_dir, project_config["name"])

    if "resource_path" in project_config:
        if os.path.isabs(project_config["resource_path"]):
            resource_path = project_config["resource_path"]
        else:
            resource_path = os.path.join(resource_dir, project_config["resource_path"])
    else:
        resource_path = os.path.join(resource_dir, project_config["name"])

    repack = Repack(src_project, project_path, resource_path, data_dir, project_config["name"])

    # register base actions
    base_action_config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "actions", "actions.json")
    repack.parse_config(project_config)
    repack.register_actions(base_action_config_file)
    repack.run(step_config)


def main():
    workpath = os.getcwd()  # os.path.dirname(os.path.realpath(__file__))

    print("workpath:%s" % workpath)

    parser = ArgumentParser()
    parser.add_argument('-s', '--src-project', dest='src_project',
                        help="original project")

    parser.add_argument('-o', '--out-dir', dest='out_dir',
                        help="pack project output path")

    parser.add_argument('-r', '--resource-dir', dest='resource_dir',
                        help="resource dir contain pack pictures and defines")

    parser.add_argument('-c', '--config-file', dest='config_file',
                        help="config file about run pack")

    parser.add_argument('-d', '--data-dir', dest='data_dir',
                        help="global data files dir")

    parser.add_argument('--step-config', dest='step_config',
                        help="step config contains actions")

    parser.add_argument('--action-config', dest='action_config',
                        help="actions config")

    args = parser.parse_args()

    print("=======================================================")

    if not os.path.isabs(args.src_project):
        args.src_project = os.path.join(workpath, args.src_project)

    if not os.path.isabs(args.resource_dir):
        args.resource_dir = os.path.join(workpath, args.resource_dir)

    if not os.path.isabs(args.out_dir):
        args.out_dir = os.path.join(workpath, args.out_dir)

    if not args.data_dir:
        args.data_dir = args.resource_dir
    else:
        if not os.path.isabs(args.data_dir):
            args.data_dir = os.path.join(workpath, args.data_dir)

    # load config info
    fp = open(args.config_file)
    config_data = json.load(fp)
    fp.close()

    # check step config
    if args.step_config:
        scfp = open(args.step_config)
        step_config = json.load(scfp)
        scfp.close()
        if "steps" in step_config:
            step_config = step_config["steps"]

    elif "steps" in config_data:
        step_config = config_data["steps"]
    else:
        raise "no step config"

    if "projects" in config_data:
        for project_config in config_data["projects"]:
            repack_project(args.src_project, args.out_dir, args.resource_dir, args.data_dir, project_config,
                           step_config, args.action_config)
    elif "project" in config_data:
        repack_project(args.src_project, args.out_dir, args.resource_dir, args.data_dir, config_data["project"],
                       step_config, args.action_config)


# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
