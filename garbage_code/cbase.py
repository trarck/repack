# -*- coding: utf-8 -*-
import os
from template_manager import TemplateManager
from generater import RandomGenerater


class CType:
    def __init__(self, name, pointer=False):
        self.name = name
        self.pointer = pointer

    def to_string(self):
        if self.pointer:
            return self.name + "*"
        else:
            return self.name

    def random_value_stringify(self):
        RandomGenerater.generate_value_stringify(self.name)


class CField:
    def __init__(self, name, ctype):
        self.name = name
        self.ctype = ctype

    def to_string(self):
        return self.ctype.to_string() + " " + self.name


class CParameter:
    def __init__(self, name, ctype):
        self.name = name
        self.ctype = ctype

    def to_string(self):
        return self.ctype.to_string() + " " + self.name


class CFunction:
    def __init__(self, name, parameters, return_type, def_template_file, code_template_file, call_template_file):
        self.name = name
        self.parameters = parameters if parameters else []
        self.return_type = return_type
        self.def_template_file = def_template_file
        self.code_template_file = code_template_file
        self.call_template_file = call_template_file

    def to_string(self):
        return self.name

    def get_def_string(self):
        tpl_folder_path = os.path.dirname(self.def_template_file)
        return TemplateManager.get_obf_data(self.def_template_file, [self, {"tpl_folder_path": tpl_folder_path}])

    def get_code_string(self):
        tpl_folder_path = os.path.dirname(self.def_template_file)
        return TemplateManager.get_obf_data(self.code_template_file, [self, {"tpl_folder_path": tpl_folder_path}])

    def get_call_string(self):
        tpl_folder_path = os.path.dirname(self.call_template_file)
        return TemplateManager.get_obf_data(self.call_template_file, [self, {"tpl_folder_path": tpl_folder_path}])


class CClass:
    def __init__(self, name, fields, methods, def_template_file):
        self.name = name
        self.fields = fields
        self.methods = methods

    def to_string(self):
        return "class " + self.name

    def to_def(self):
        return "class  {};"
