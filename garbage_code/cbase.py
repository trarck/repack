# -*- coding: utf-8 -*-
import os
import random
from template_manager import TemplateManager
from generater import RandomGenerater


class CType(object):
    def __init__(self, name, pointer=False):
        self.name = name
        self.pointer = pointer

    def to_string(self):

        if not self.name:
            return ""

        if self.pointer:
            return self.name + "*"
        else:
            return self.name

    def random_value_stringify(self):
        return RandomGenerater.generate_value_stringify(self.name)

    def is_void(self):
        if self.name:
            if self.name == "void":
                return True
            else:
                return False
        else:
            return True


class CField(object):
    def __init__(self, name, ctype, tpl_folder_path):
        self.name = name
        self.ctype = ctype
        self.tpl_folder_path = tpl_folder_path
        self._init_template_files()

    def _init_template_files(self):
        self.def_template_file = os.path.join(self.tpl_folder_path, "field.tpl")
        self.call_template_file = os.path.join(self.tpl_folder_path, "field_call.tpl")

    def to_string(self):
        return TemplateManager.get_data(self.def_template_file, [self])

    def get_call_string(self, inst_name=None):
        return TemplateManager.get_data(self.call_template_file, [self, {"class_inst": inst_name}])


class CParameter(object):
    def __init__(self, name, ctype, prev=None):
        self.name = name
        self.ctype = ctype
        self.prev = prev if prev else name

    def to_string(self):
        return self.ctype.to_string() + " " + self.name


class CFunction(object):
    def __init__(self, name, parameters, return_type, tpl_folder_path):
        self.name = name
        self.parameters = parameters if parameters else []
        self.return_type = return_type
        self.tpl_folder_path = tpl_folder_path

        self.calls = []
        self.base_code = None

        self._init_template_files()

    def _init_template_files(self):
        self.def_template_file = os.path.join(self.tpl_folder_path, "function_def.tpl")
        self.code_template_file = os.path.join(self.tpl_folder_path, "function_code.tpl")
        self.call_template_file = os.path.join(self.tpl_folder_path, "function_call.tpl")

    def call(self, other):
        self.calls.append(other)

    def to_string(self):
        return self.name

    @property
    def full_name(self):
        return self.name

    def get_def_string(self):
        return TemplateManager.get_data(self.def_template_file, [self])

    def get_code_string(self):
        return TemplateManager.get_data(self.code_template_file, [self])

    def get_call_string(self, inst_name=None):
        return TemplateManager.get_data(self.call_template_file, [self, {"class_inst": inst_name}])


class CClass(object):
    def __init__(self, name, fields, methods, tpl_folder_path):
        self.name = name
        self.fields = fields if fields else []
        # 不包含类的构造函数和析构函数。
        self.methods = methods if methods else []
        self.tpl_folder_path = tpl_folder_path
        self._init_template_files()

    def _init_template_files(self):
        self.def_template_file = os.path.join(self.tpl_folder_path, "class_def.tpl")
        self.code_template_file = os.path.join(self.tpl_folder_path, "class_code.tpl")
        self.stack_instance_def_template_file = os.path.join(self.tpl_folder_path, "class_stack_instance.tpl")
        self.need_includes_template_file = os.path.join(self.tpl_folder_path, "class_need_includes.tpl")

    def add_method(self, method):
        self.methods.append(method)
        method.cpp_class = self

    @property
    def full_name(self):
        return self.name

    def to_string(self):
        return "class " + self.name

    def get_def_string(self,implement_construct_destruct=False):
        return TemplateManager.get_data(self.def_template_file, [self,{"implement_construct_destruct":implement_construct_destruct}])

    def get_code_string(self, contain_methods=True):
        return TemplateManager.get_data(self.code_template_file, [self, {"contain_methods": contain_methods}])

    def get_stack_instance_def(self, inst_name):
        return TemplateManager.get_data(self.stack_instance_def_template_file, [self, {"inst_name": inst_name}])

    def get_need_includes(self):
        return TemplateManager.get_data(self.need_includes_template_file, [self])

    def get_call_field_codes(self, inst_name, count):
        """
        随机生成指定条访问类的属性的指令
        :param inst_name:
        :param count:
        :return:
        """
        codes = []
        for _ in range(count):
            codes.append(random.choice(self.fields).get_call_string(inst_name))

    def get_call_methods_codes(self, inst_name, count):
        """
        随机生成指定条访问类的属性和方法的指令
        :param inst_name:
        :param count:
        :return:
        """
        codes = []
        for _ in range(count):
            codes.append(random.choice(self.fields).get_call_string(inst_name))

    def get_call_codes(self, inst_name, count):
        """
        随机生成指定条访问类的属性和方法的指令
        :param inst_name:
        :param count:
        :return:
        """
        codes = []
        for _ in range(count):
            if random.randint(0, 9) > 4:
                codes.append(random.choice(self.fields).get_call_string(inst_name))
            else:
                codes.append(random.choice(self.methods).get_call_string(inst_name))
        return codes