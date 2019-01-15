# -*- coding: utf-8 -*-
import os
from generater import RandomGenerater
from objc_generator import ObjcGenerator
from cfile import CFile
from c_garbage_code import CGarbageCode
import gc_utils


class ObjcFile(CFile):

    def prepare(self):
        # check class name
        if not self.class_name:
            self.class_name = RandomGenerater.generate_string(8, 32)
            self.class_name = self.class_name[0].upper() + self.class_name[1:]

        objc_class = ObjcGenerator.generate_class(self.tpl_folder_path, self.config["field_count"],
                                                  self.config["method_count"], self.config["parameter_count"],
                                                  self.config["return_probability"], self.class_name)

        if "call_others" in self.config and self.config["call_others"]:
            for i in range(len(objc_class.methods) - 1):
                objc_class.methods[i].call(objc_class.methods[i + 1])

        self.c_class = objc_class


class ObjCGarbageCode(CGarbageCode):
    def __init__(self, tpl_folder_path):
        """
        生成objc的类
        :param tpl_folder_path:
        """
        super(ObjCGarbageCode, self).__init__(tpl_folder_path)
        self.source_file_ext = ".mm"

    def generate_file(self, out_folder_path, class_index):
        class_name = RandomGenerater.generate_string_first_upper(8, 16)
        head_file_name = os.path.join(out_folder_path, class_name + ".h")
        source_file_name = os.path.join(out_folder_path, class_name + self.source_file_ext)
        self.generated_files.append(head_file_name)
        self.generated_files.append(source_file_name)
        self.generated_head_files.append(class_name + ".h")

        field_count = gc_utils.get_range_count("field_count", self.config, 3)
        method_count = gc_utils.get_range_count("method_count", self.config, 5)
        parameter_count = gc_utils.get_range_count("parameter_count", self.config, 3)
        return_probability = gc_utils.get_range_count("return_probability", self.config, 5)

        generator = ObjcFile({
            "head_file": head_file_name,
            "source_file": source_file_name,
            "tpl_folder": self.tpl_folder_path,
            "class_name": class_name,
            "field_count": field_count,
            "method_count": method_count,
            "parameter_count": parameter_count,
            "return_probability": return_probability,
            "call_others": self.generate_config["call_others"],
            "search_path": self.generate_config["search_path"]
        })

        generator.prepare()
        generator.generate_code()
        return generator.get_class_execute_chain()
