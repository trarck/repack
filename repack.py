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
import generater
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
            self.crypt_info.key = generater.RandomGenerater.generate_key()

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

    def run(self, steps, executes=None, ignores=None):
        # if self.need_copy_project:
        #     self.copy_project()

        if executes or ignores:
            steps = self.filter_steps(steps, executes, ignores)

        self.do_steps(steps)

    def filter_steps(self, steps, executes=None, ignores=None):
        filtered = []
        for step_data in steps:
            if ignores:
                if step_data["name"] not in ignores:
                    if executes:
                        if step_data["name"] in executes:
                            filtered.append(step_data)
                    else:
                        filtered.append(step_data)
            else:
                if executes:
                    if step_data["name"] in executes:
                        filtered.append(step_data)
                else:
                    filtered.append(step_data)

        return filtered

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
            raise Exception("Can't find action %s" % action_data["name"])

    # run as give step name[id] sequence
    def run2(self, steps, executes=None, ignores=None):
        # if self.need_copy_project:
        #     self.copy_project()

        if isinstance(steps, list):
            step_map = {}
            for step_data in steps:
                if ignores is None or step_data["name"] not in ignores:
                    step_map[step_data["name"]] = step_map
            steps = step_map

        self._execute(executes, steps)

    def _execute(self, executes, steps):
        for step_name in executes:
            if step_name in steps:
                self.do_step(steps[step_name])

    # def copy_project(self, config=None):
    #     print("copy project from %s to %s" % (self.matrix_project_root_path, self.project_root_path))
    #     if os.path.exists(self.matrix_project_root_path):
    #         if os.path.exists(self.project_root_path):
    #             shutil.rmtree(self.project_root_path)
    #         shutil.copytree(self.matrix_project_root_path, self.project_root_path, True)
    #     else:
    #         print("copy project error no %s folder " % self.matrix_project_root_path)


def repack_project(src_project, out_dir, resource_dir, data_dir, project_config, step_config, ext_action_file, actions,
                   ignore_actions):
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

    repack.parse_config(project_config)

    # register base actions
    base_action_config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "actions", "actions.json")
    repack.register_actions(base_action_config_file)

    if ext_action_file:
        repack.register_actions(ext_action_file)

    repack.run(step_config)


def parse_words(args):
    # load extend words
    if args.words_file and os.path.exists(args.words_file):
        generater.WordsManager.load_words(args.words_file)

    if args.class_words_file and os.path.exists(args.class_words_file):
        generater.WordsManager.load_class_words(args.class_words_file)

    if args.filed_words_file and os.path.exists(args.filed_words_file):
        generater.WordsManager.load_field_words(args.filed_words_file)

    if args.function_words_file and os.path.exists(args.function_words_file):
        generater.WordsManager.load_function_words(args.function_words_file)


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

    parser.add_argument('--words-file', dest='words_file',
                        help="words data file")

    parser.add_argument('--class-words-file', dest='class_words_file',
                        help="words data file")

    parser.add_argument('--filed-words-file', dest='filed_words_file',
                        help="words data file")

    parser.add_argument('--function-words-file', dest='function_words_file',
                        help="words data file")

    parser.add_argument('steps', nargs='*',
                        help="steps to run")

    parser.add_argument('-i', '--ignore-steps', dest='ignore_steps',
                        help="actions not run")

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
        raise Exception("no step config")

    # load base words
    generater.WordsManager.init_words()

    parse_words(args)

    if "projects" in config_data:
        for project_config in config_data["projects"]:
            repack_project(args.src_project, args.out_dir, args.resource_dir, args.data_dir, project_config,
                           step_config, args.action_config, args.steps, args.ignore_steps)
    elif "project" in config_data:
        repack_project(args.src_project, args.out_dir, args.resource_dir, args.data_dir, config_data["project"],
                       step_config, args.action_config, args.steps, args.ignore_steps)


# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
