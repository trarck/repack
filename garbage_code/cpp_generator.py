# -*- coding: utf-8 -*-
from cpp_base import *


class CppGenerator:
    def __init__(self, tpl_folder_path):
        """
        c++相关的生成器
        :param tpl_folder_path:
        """
        self.tpl_folder_path = tpl_folder_path

    @staticmethod
    def generate_field(field_name=None, field_type=None):
        if not field_name:
            field_name = RandomGenerater.generate_string()
        if not field_type:
            field_type = CType(RandomGenerater.generate_cpp_type())
        return CField(field_name, field_type)

    @staticmethod
    def generate_parameter(param_name=None):
        if not param_name:
            param_name = RandomGenerater.generate_string()
        param_type = CType(RandomGenerater.generate_cpp_type())
        return CParameter(param_name, param_type)

    @staticmethod
    def generate_function(tpl_folder_path, max_parameter_count=0, return_probability=30, method_name=None):
        if not method_name:
            method_name = RandomGenerater.generate_string()

        parameters = []
        if max_parameter_count > 0:
            parameter_count = random.randint(0, max_parameter_count)
            for i in range(parameter_count):
                parameter = CppGenerator.generate_parameter()
                parameters.append(parameter)

        # 30% create return type
        if random.randint(0, 100) <= return_probability:
            return_type = CType(RandomGenerater.generate_cpp_type())
        else:
            return_type = CType("void")

        return CppMethod(method_name, parameters, return_type, tpl_folder_path)

    @staticmethod
    def generate_class(tpl_folder_path, field_count, method_count, max_parameter, method_return_probability,
                       namespace=None, class_name=None):
        # gen fields
        fields = None
        if field_count > 0:
            fields = []
            for i in range(field_count):
                fields.append(CppGenerator.generate_field())

        if not class_name:
            class_name = RandomGenerater.generate_string()
            class_name = class_name[0].upper() + class_name[1:]

        cpp_class = CppClass(class_name, fields, None, tpl_folder_path, namespace)

        # gen methods
        methods = None
        if method_count > 0:
            methods = []

            for i in range(method_count):
                method = CppGenerator.generate_function(tpl_folder_path, max_parameter, method_return_probability)
                method.cpp_class = cpp_class
                methods.append(method)

        cpp_class.methods = methods
        return cpp_class
