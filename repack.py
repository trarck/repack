import os
import sys
import traceback
import shutil
import random
import json

from argparse import ArgumentParser
from resource_obfuscator import ResourceObfuscator, CryptInfo
from project import IosProject
import utils


class Repack:
    def __init__(self, matrix_project_root_path, project_root_path, pack_resource_path, name):
        self.matrix_project_root_path = matrix_project_root_path
        self.project_root_path = project_root_path
        self.pack_resource_path = pack_resource_path
        self.name = name
        self.crypt_info = CryptInfo(None, "md5")
        self.need_copy_project = True

        self._config_data = None

    def _parse_config(self, conf_data):
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

    def run(self, config, steps):
        self._parse_config(config)

        if self.need_copy_project:
            self.copy_project()

        self.do_steps(steps)

    def do_steps(self, steps):
        for action_data in steps:
            self.do_action(action_data)

    # def do_step(self, step_data):
    #     print("===> do step %s" % step_data["name"])
    #     self.current_step = step_data
    #     self.do_actions(step_data["actions"])
    #
    # def do_actions(self, actions):
    #     for action in actions:
    #         self.do_action(action)

    def do_action(self, action_data):
        print("===> do action %s" % action_data["name"])
        try:
            fun = getattr(self, action_data["name"])
        except AttributeError:
            raise "Can't find action %s" % action_data["name"]

        fun(action_data)

    def copy_project(self):
        print("copy project from %s to %s"%(self.matrix_project_root_path,self.project_root_path))
        if os.path.exists(self.matrix_project_root_path):
            if os.path.exists(self.project_root_path):
                shutil.rmtree(self.project_root_path)
            shutil.copytree(self.matrix_project_root_path, self.project_root_path)
        else:
            print("copy project error no %s folder " % self.matrix_project_root_path)

    def copy_files(self, config):
        print("===>copy file from %s to %s"%(config["from"],config["to"]))
        utils.copy_files_with_config(config, self.pack_resource_path, self.project_root_path)

    def set_xcode_project(self, config):
        xcode_project_path = self._config_data["xcode_project_path"]
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.project_root_path, xcode_project_path)

        package_id = self._config_data["package_id"]

        if "target_name" in self._config_data:
            target_name = self._config_data["target_name"]

        else:
            target_name = self.name

        if "display_name" in self._config_data:
            display_name = self._config_data["display_name"]
        else:
            display_name=target_name

        xcode_project_name = None
        if "xcode_project_name" in self._config_data:
            xcode_project_name = self._config_data["xcode_project_name"]

        product_name = None
        if "product_name" in self._config_data:
            product_name = self._config_data["product_name"]

        ios_project = IosProject(xcode_project_path)
        ios_project.rename(target_name, package_id, display_name, xcode_project_name, product_name)
        ios_project.set_resource_obfuscate_key(self.crypt_info.key)

    def obfuscate_resources(self, config):
        res_path = config["res_path"]
        if not os.path.isabs(res_path):
            res_path = os.path.join(self.project_root_path, res_path)

        sub_dirs = None
        if "sub_dirs" in config:
            sub_dirs = config["sub_dirs"]

        remove_source = True
        if "remove_source" in config:
            remove_source = config["remove_source"]

        if "out_path" in config:
            out_path = config["out_path"]
            if not os.path.isabs(out_path):
                out_path = os.path.join(self.project_root_path, out_path)
        else:
            out_path = res_path

        res_obf = ResourceObfuscator(res_path, out_path, sub_dirs, self.crypt_info, remove_source)
        res_obf.start()


def main():
    workpath = os.path.dirname(os.path.realpath(__file__))

    parser = ArgumentParser()
    parser.add_argument('-s', '--src-project', dest='src_project',
                        help="original project")

    parser.add_argument('-o', '--out-dir', dest='out_dir',
                        help="pack project output path")

    parser.add_argument('-r', '--resource-dir', dest='resource_dir',
                        help="resource dir contain pack pictures and defines")

    parser.add_argument('-c', '--config-file', dest='config_file',
                        help="config file about run pack")

    args = parser.parse_args()

    print("=======================================================")

    # get pack info
    fp = open(args.config_file)
    config_data = json.load(fp)
    fp.close()

    if "projects" in config_data:
        for project_config in config_data["projects"]:

            if "project_path" in project_config:
                project_path = os.path.join(args.out_dir, project_config["project_path"])
            else:
                project_path = os.path.join(args.out_dir, project_config["name"])

            if "resource_path" in project_config:
                resource_path = os.path.join(args.resource_dir, project_config["resource_path"])
            else:
                resource_path = os.path.join(args.resource_dir, project_config["name"])

            repack = Repack(args.src_project, project_path, resource_path,project_config["name"])

            repack.run(project_config, config_data["steps"])


# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
