# -*- coding: utf-8 -*-
from garbage_code.cbase import *


class ObjcMethod(CFunction):
    def __init__(self, name, parameters, return_type, tpl_folder_path, objc_class=None):
        super(ObjcMethod, self).__init__(name, parameters, return_type, tpl_folder_path)
        self.objc_class = objc_class

    @property
    def full_name(self):
        if self.objc_class:
            return self.objc_class.name + "::" + self.name
        else:
            return self.name

    def get_call_string(self, inst_name=None):
        return TemplateManager.get_data(self.call_template_file, [self, {"class_inst": inst_name}])


class ObjcClass(CClass):

    @property
    def full_name(self):
        if self.namespace:
            return self.namespace + "::" + self.name
        return self.name

