# -*- coding: utf-8 -*-
import random
from objc_base import *

from generater import RandomGenerater

objc_method_parameter_prevs = ["with", "did", "open", "can"]
objc_method_parameter_prevs_length = len(objc_method_parameter_prevs)

name_prev_words = ["All", "One", "Dynamic", "Static"]
name_prev_words_lenth = len(name_prev_words)
name_main_words = ["User", "Account", "Update", "Card", "Deck", "Npc", "Unit", "Controller", "Manager", "System",
                   "Data", "Output", "Input"]
name_main_words_lenth = len(name_main_words)

field_prev_words = ["input", "output", "blue", "red", "green"]
field_prev_words_lenth = len(field_prev_words)
field_main_words = ["Size", "Color", "Range", "Radius", "Scale", "Center", "Width", "Height", "Framebuffer", "Duration",
                    "Average", "Processing", "Finished", "Block", "Options"]
field_main_words_lenth = len(field_main_words)

function_prev_words = ["with", "did", "check", "change", "set"]
function_prev_words_lenth = len(function_prev_words)
function_main_words = ["Size", "Color", "Range", "Radius", "Scale", "Center", "Width", "Height", "Framebuffer",
                       "Duration",
                       "Average", "Processing", "Finished", "Block", "Options", "With"]
function_main_words_lenth = len(function_main_words)


class ObjcGenerator:
    def __init__(self, tpl_folder_path):
        """
        objc相关的生成器
        :param tpl_folder_path:
        """
        self.tpl_folder_path = tpl_folder_path

    @staticmethod
    def generate_rule_name(random_prev_length=3, random_end_length=3, max_word=5, prev_probability=10):
        name = RandomGenerater.generate_string_first_upper(random_prev_length, random_prev_length)
        if random.randint(0, 100) < prev_probability:
            name += name_prev_words[random.randint(0, name_prev_words_lenth - 1)]

        word_count = random.randint(1, max_word)
        for _ in range(word_count):
            name += name_main_words[random.randint(0, name_main_words_lenth - 1)]

        name += RandomGenerater.generate_string_first_upper(random_end_length, random_end_length)
        return name

    @staticmethod
    def generate_field_name(random_prev_length=3, random_end_length=3, max_word=5, prev_probability=10,
                            auto_add_prev_probability=20):
        name = ""
        if random.randint(0, 100) < prev_probability:
            name += field_prev_words[random.randint(0, field_prev_words_lenth - 1)]
        elif random_prev_length > 0 and random.randint(0, 100) < auto_add_prev_probability:
            name += RandomGenerater.generate_string_first_lower(random_prev_length, random_prev_length)

        word_count = random.randint(1, max_word)
        indexs = range(field_main_words_lenth)

        for i in range(word_count):
            indx = random.randint(0, field_main_words_lenth - 1 - i)
            name += field_main_words[indexs[indx]]
            indexs[indx] = indexs[-1 - i]

        if random_end_length > 0:
            name += RandomGenerater.generate_string_first_upper(random_end_length, random_end_length)

        return name[0].lower() + name[1:]

    @staticmethod
    def generate_function_name(random_prev_length=3, random_end_length=3, max_word=5, prev_probability=10,
                               auto_add_prev_probability=80):
        name = ""
        if random.randint(0, 100) < prev_probability:
            name += function_prev_words[random.randint(0, function_prev_words_lenth - 1)]
        elif random_prev_length > 0 and random.randint(0, 100) < auto_add_prev_probability:
            name += RandomGenerater.generate_string_first_lower(random_prev_length, random_prev_length)

        word_count = random.randint(1, max_word)

        indexs = range(function_main_words_lenth)

        for i in range(word_count):
            indx = random.randint(0, function_main_words_lenth - 1 - i)
            name += function_main_words[indexs[indx]]
            indexs[indx] = indexs[-1 - i]

        if random_end_length > 0:
            name += RandomGenerater.generate_string_first_upper(random_end_length, random_end_length)
        return name[0].lower() + name[1:]

    @staticmethod
    def get_random_parameter_prev():
        return objc_method_parameter_prevs[random.randint(0, objc_method_parameter_prevs_length - 1)]

    @staticmethod
    def generate_field(tpl_folder_path, field_name=None, field_type=None):
        if not field_name:
            field_name = ObjcGenerator.generate_field_name(2, 3)
        if not field_type:
            field_type = CType(RandomGenerater.generate_objc_type())
        return CField(field_name, field_type, tpl_folder_path)

    @staticmethod
    def generate_parameter(param_name=None, param_type=None):
        if not param_name:
            param_name = ObjcGenerator.generate_function_name(0, 0)
        if not param_type:
            param_type = CType(RandomGenerater.generate_objc_type())
        return CParameter(param_name, param_type)

    @staticmethod
    def generate_function(tpl_folder_path, max_parameter_count=0, return_probability=30, method_name=None):
        if not method_name:
            method_name = ObjcGenerator.generate_function_name(0, 2, 3, 50)
        parameters = []
        if max_parameter_count > 0:
            parameter_count = random.randint(0, max_parameter_count)
            for i in range(parameter_count):
                parameter = ObjcGenerator.generate_parameter()
                if i > 0:
                    parameter.prev = ObjcGenerator.get_random_parameter_prev() + parameter.name
                parameters.append(parameter)

        if random.randint(0, 100) <= return_probability:
            return_type = CType(RandomGenerater.generate_objc_type())
        else:
            return_type = CType(None)

        return ObjcMethod(method_name, parameters, return_type, tpl_folder_path)

    @staticmethod
    def generate_class(tpl_folder_path, field_count, method_count, max_parameter, method_return_probability,
                       class_name=None):
        # gen fields
        fields = None
        if field_count > 0:
            fields = []
            for i in range(field_count):
                fields.append(ObjcGenerator.generate_field(tpl_folder_path))

        if not class_name:
            class_name = RandomGenerater.generate_string()
            class_name = class_name[0].upper() + class_name[1:]

        objc_class = ObjcClass(class_name, fields, None, tpl_folder_path)

        # gen methods
        methods = None
        if method_count > 0:
            methods = []

            for i in range(method_count):
                method = ObjcGenerator.generate_function(tpl_folder_path, max_parameter, method_return_probability)
                method.objc_class = objc_class
                methods.append(method)

        objc_class.methods = methods
        return objc_class
