# -*- coding: utf-8 -*-
import os

from pbxproj import XcodeProject
from Cheetah.Template import Template
from generater import RandomGenerater
import gc_utils


class CGarbageCode(object):
    def __init__(self, tpl_folder_path):
        """
        生成垃圾代码
        目前主要生成c++的类。
        :param tpl_folder_path:
        """
        self.tpl_folder_path = tpl_folder_path.encode("utf-8")
        self.generate_config = None
        self.inject_config = None
        self._inject_checked_files = None
        self._injected_files = None
        self.source_file_ext = ".c"

        self.generated_files = []
        self.generated_head_files = []

    def _get_xcode_project_file_path(self, project_dir):
        if project_dir.find(".xcodeproj") > -1:
            return project_dir

        files = os.listdir(project_dir)
        for filename in files:
            if filename.find(".xcodeproj") > -1:
                return os.path.join(project_dir, filename)
        return None

    def prepare_config(self, out_folder_path):

        gen_file_count = gc_utils.get_range_count("generate_file_count", self.generate_config, 6)

        if "group_name" not in self.generate_config:
            self.generate_config["group_name"] = RandomGenerater.generate_string(6, 10)

        if "call_others" not in self.generate_config:
            self.generate_config["call_others"] = True

        if "search_path" not in self.generate_config:
            self.generate_config["search_path"] = out_folder_path

        if "namespace" in self.generate_config:
            if not self.generate_config["namespace"]:
                self.generate_config["namespace"] = RandomGenerater.generate_string(5, 8).lower()

        return gen_file_count

    def generate_files(self, out_folder_path, xcode_project_path, exec_code_file_path, generate_config):
        self.generate_config = generate_config

        gen_file_count = self.prepare_config(out_folder_path)

        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

        self.generated_files = []
        self.generated_head_files = []

        call_generate_codes = []
        class_index = 1

        for i in range(gen_file_count):
            call_generate_func = self.generate_file(out_folder_path, class_index)
            call_generate_codes.append(call_generate_func)
            class_index += 1

        auto_all_name, auto_all_function = self.generate_call_file_for_files(self, out_folder_path, call_generate_codes)

        return self.add_generated_files_to_xcode_project(generate_config, exec_code_file_path, auto_all_name,
                                                         auto_all_function, xcode_project_path)

    def generate_file(self, out_folder_path, class_index):
        return "must do in child"

    def generate_call_file_for_files(self, out_folder_path, call_generate_codes):
        """
        使用一个文件引用生成的文件
        :param out_folder_path:
        :param generate_config:
        :param call_generate_codes:
        :return:
        """
        # generate call generated code prevent delete by link optimization
        exec_once_tpl = Template(file=os.path.join(self.tpl_folder_path, "exec_code_once.tpl"),
                                 searchList=[{"code": "".join(call_generate_codes),
                                              "prefix": RandomGenerater.generate_string()}])
        exec_once = str(exec_once_tpl)

        if "generate_executor" in self.generate_config and self.generate_config["generate_executor"]:
            print("generate a executor")
        else:
            print("insert into execute file")
            include_heads = "\n"
            for head_file in self.generated_head_files:
                include_heads += "#include \"%s\"\n" % head_file

        auto_all_name = RandomGenerater.generate_string(20, 30)
        auto_all_function = RandomGenerater.generate_string(20, 30)
        auto_all_head_file = os.path.join(out_folder_path, auto_all_name + ".h")
        auto_all_source_file = os.path.join(out_folder_path, auto_all_name + ".cpp")
        self.generated_files.append(auto_all_head_file)
        self.generated_files.append(auto_all_source_file)

        auto_all_head_tpl = Template(file=os.path.join(self.tpl_folder_path, "auto_all_head.tpl"),
                                     searchList=[{"name": auto_all_name, "headers": include_heads,
                                                  "auto_all_function": auto_all_function}])

        auto_all_source_tpl = Template(file=os.path.join(self.tpl_folder_path, "auto_all_source.tpl"),
                                       searchList=[{"name": auto_all_name, "code": exec_once,
                                                    "auto_all_function": auto_all_function}])

        fp = open(auto_all_head_file, "w+")
        fp.write(str(auto_all_head_tpl))
        fp.close()

        fp = open(auto_all_source_file, "w+")
        fp.write(str(auto_all_source_tpl))
        fp.close()

        return auto_all_name, auto_all_function

    def add_generated_files_to_xcode_project(self, exec_code_file_path, auto_all_name,
                                             auto_all_function, xcode_project_path):
        """
        把生成的文件加入xcode工程
        :param generate_config:
        :param exec_code_file_path:
        :param auto_all_name:
        :param auto_all_function:
        :param xcode_project_path:
        :param group_name:
        :param search_path:
        :return:
        """
        group_name = self.generate_config["group_name"]

        search_path = self.generate_config["search_path"]

        # create action execute in repack
        insert_head_action = {
            "operation": "insert",
            "file_path": exec_code_file_path,
            "keys": self.generate_config["include_insert_keys"],
            "words": "\n#include \"%s.h\"\n" % auto_all_name
        }
        insert_code_action = {
            "operation": "insert",
            "file_path": exec_code_file_path,
            "keys": self.generate_config["code_insert_keys"],
            "words": "\n%s();\n" % auto_all_function
        }
        modify_exec_code_actions = {
            "name": "modify_files",
            "files": [insert_head_action, insert_code_action]
        }

        # add generated files to xcode project

        pbx_proj_file_path = os.path.join(self._get_xcode_project_file_path(xcode_project_path), "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        # add out dir to head search path
        pbx_project.add_header_search_paths(search_path)
        # add a group
        group = pbx_project.add_group(group_name)
        # add files
        for file_path in self.generated_files:
            pbx_project.add_file(file_path, group)
        pbx_project.save()

        return modify_exec_code_actions
