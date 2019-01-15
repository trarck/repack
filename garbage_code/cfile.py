# -*- coding: utf-8 -*-
import os

from pbxproj import XcodeProject
from Cheetah.Template import Template
from generater import RandomGenerater
from cpp_generator import CppGenerator
import gc_utils


class CFile(object):
    def __init__(self, config):
        """
        生成类的头文件和源文件
        :param config:
        """
        self.head_file_path = config["head_file"]
        self.source_file_path = config["source_file"]
        self.tpl_folder_path = config["tpl_folder"]
        if "search_path" in config and config["search_path"]:
            self.search_path = config["search_path"]
        else:
            self.search_path = os.path.dirname(self.head_file_path)

        self.class_name = None
        if "class_name" in config:
            class_name = config["class_name"]
            cs = class_name.split('.')
            self.class_name = cs[-1]
            del cs[-1]
            self.namespace = cs

        if "namespace" in config:
            self.namespace = config["namespace"]
        else:
            self.namespace = None
        self.config = config

        self.generated_methods = []
        self.generated_fields = []
        self.headers = []
        self.head_headers = config["head_headers"] if "head_headers" in config else []
        self.source_headers = config["source_headers"] if "source_headers" in config else []

        self.c_class = None
        self.head_fp = None
        self.source_fp = None

    def prepare(self):
        # check class name
        if not self.class_name:
            self.class_name = RandomGenerater.generate_string(8, 32)
            self.class_name = self.class_name[0].upper() + self.class_name[1:]

        c_class = CppGenerator.generate_class(self.tpl_folder_path, self.config["field_count"],
                                              self.config["method_count"], self.config["parameter_count"],
                                              self.config["return_probability"], self.class_name)

        if "call_others" in self.config and self.config["call_others"]:
            for i in range(len(c_class.methods) - 1):
                c_class.methods[i].call(c_class.methods[i + 1])

        self.c_class = c_class

    def generate_code(self):
        # gen class string
        class_define_string = self.c_class.get_need_includes()
        class_define_string += self.c_class.get_def_string()

        class_impl_str = self.c_class.get_code_string()

        self.headers.append(self.head_file_path)
        # gen head
        head_tpl = Template(file=os.path.join(self.tpl_folder_path, "layout_head.tpl"),
                            searchList=[self, {"class_define": class_define_string}])

        source_tpl = Template(file=os.path.join(self.tpl_folder_path, "layout_source.tpl"),
                              searchList=[self, {"class_code": class_impl_str}])

        # write to file
        if not os.path.exists(os.path.dirname(self.head_file_path)):
            os.makedirs(os.path.dirname(self.head_file_path))
        if not os.path.exists(os.path.dirname(self.source_file_path)):
            os.makedirs(os.path.dirname(self.source_file_path))

        self.head_fp = open(self.head_file_path, "w+")
        self.source_fp = open(self.source_file_path, "w+")

        self.head_fp.write(str(head_tpl))
        self.source_fp.write(str(source_tpl))

        self.head_fp.close()
        self.source_fp.close()

    def get_class_execute_chain(self, class_index):
        inst_name = "%s_%d" % (RandomGenerater.generate_string(), class_index)
        inst_declare = self.c_class.get_stack_instance_def(inst_name)
        call_str = self.c_class.methods[0].method.get_call_string(inst_name)
        return inst_declare + call_str
