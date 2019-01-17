# -*- coding: utf-8 -*-
from garbage_code.cbase import *


class CppMethod(CFunction):
    def __init__(self, name, parameters, return_type, tpl_folder_path, cpp_class=None):
        super(CppMethod, self).__init__(name, parameters, return_type, tpl_folder_path)
        self.cpp_class = cpp_class

    @property
    def full_name(self):
        if self.cpp_class:
            return self.cpp_class.name + "::" + self.name
        else:
            return self.name


class CppClass(CClass):
    def __init__(self, name, fields, methods, tpl_folder_path, namespace):
        super(CppClass, self).__init__(name, fields, methods, tpl_folder_path)
        self.namespace = namespace

    @property
    def full_name(self):
        if self.namespace:
            return self.namespace + "::" + self.name
        return self.name

