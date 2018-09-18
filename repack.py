import os
import sys
import traceback
import shutil
import random
import json
from string import Template

from argparse import ArgumentParser
from resource_obfuscator import ResourceObfuscator, CryptInfo
from project import IosProject
from source_file import SourceFile
from file_crypt import FileCrypt
import utils


class Repack:
    def __init__(self, matrix_project_root_path, project_root_path, pack_resource_path, global_data_dir, name):
        self.matrix_project_root_path = matrix_project_root_path
        self.project_root_path = project_root_path
        self.pack_resource_path = pack_resource_path
        self.global_data_dir = global_data_dir
        self.name = name
        self.crypt_info = CryptInfo(None, "md5")
        self.need_copy_project = True

        self._config_data = None

        self._environment = {
            u"MATRIX_PROJECT_ROOT": self.matrix_project_root_path,
            u"PROJECT_ROOT": self.project_root_path,
            u"PACK_RESOURCE_ROOT": self.pack_resource_path,
            u"GLOBAL_DATA_DIR": self.global_data_dir
        }

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

        self._merge_environment(conf_data, "PROJECT")

    def run(self, config, steps):
        self._parse_config(config)

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
        try:
            fun = getattr(self, action_data["name"])
        except AttributeError:
            raise "Can't find action %s" % action_data["name"]

        fun(action_data)

    def copy_project(self):
        print("copy project from %s to %s" % (self.matrix_project_root_path, self.project_root_path))
        if os.path.exists(self.matrix_project_root_path):
            if os.path.exists(self.project_root_path):
                shutil.rmtree(self.project_root_path)
            shutil.copytree(self.matrix_project_root_path, self.project_root_path)
        else:
            print("copy project error no %s folder " % self.matrix_project_root_path)

    def copy_files(self, config):
        print("===>copy file from %s to %s" % (self.translate_string(config["from"]), self.translate_string(config["to"])))
        config["from"] = self.translate_string(config["from"])
        config["to"] = self.translate_string(config["to"])
        utils.copy_files_with_config(config, self.pack_resource_path, self.project_root_path)

    def delete_files(self,config):
        print("===>delete files ")
        for file_path in config[files]:
            file_path=self.translate_string(file_path)
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
                    source.replace(modify_config["froms"], modify_config["tos"], words)
                elif operation == "replace_after":
                    source.replace_after(modify_config["froms"], modify_config["tos"], words)
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
            
        code_sign_identity=self.translate_string(config["code_sign_identity"])
        provisioning_profile=self.translate_string(config["provisioning_profile"])
        
        development_team=None
        if "development_team" in config:
            development_team=self.translate_string(config["development_team"])
            
        provisioning_profile_uuid=None
        if "provisioning_profile_uuid" in config:
            provisioning_profile_uuid=self.translate_string(config["provisioning_profile_uuid"])
        
        code_sign_entitlements=None
        if "code_sign_entitlements" in config:
            code_sign_entitlements=self.translate_string(config["code_sign_entitlements"])
        
        ios_project = IosProject(xcode_project_path)
        ios_project.rename(target_name, package_id, display_name, xcode_project_name, product_name)
        #ios_project.set_resource_obfuscate_key(self.crypt_info.key)
        ios_project.set_code_sign(code_sign_identity,provisioning_profile,development_team,provisioning_profile_uuid,code_sign_entitlements)
    
    def crypt_files(self, config):
        from_dir = self.translate_string(config["from"])
        if not os.path.isabs(from_dir):
            from_dir = os.path.join(self.project_root_path, from_dir)

        if "to" in config:
            to_dir = self.translate_string(config["to"])
            if not os.path.isabs(from_dir):
                to_dir = os.path.join(self.project_root_path, to_dir)
        else:
            to_dir = from_dir

        if "key" in config:
            key = self.translate_string(config["key"])
        else:
            key = self._config_data["xxtea_key"]

        if "sign" in config:
            sign = self.translate_string(config["sign"])
        else:
            sign = self._config_data["xxtea_sign"]

        include = None
        if "include" in config:
            include = utils.convert_rules(config["include"])

        fcrypt = FileCrypt(key, sign)
        fcrypt.encrypt_dir(from_dir, to_dir, include)

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
            args.data_dir = os.path.join(workpath, args.resource_dir)

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

            repack = Repack(args.src_project, project_path, resource_path, args.data_dir, project_config["name"])

            repack.run(project_config, config_data["steps"])


# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
