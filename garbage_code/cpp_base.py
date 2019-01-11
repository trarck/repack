# -*- coding: utf-8 -*-
import random
from garbage_code.cbase import *


class CppMethod(CFunction):

    def to_code(self):
        return "cpp class"


class CppClass(CClass):
    def __init__(self, name, fields, methods, def_template_file,namespace):
        super(CClass, self).__init__(name, fields, methods,def_template_file)
        self.namespace = namespace

    def to_code(self):
        return "cpp class"
