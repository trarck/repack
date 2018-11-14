# -*- coding: utf-8 -*-
import os
import random

from Cheetah.Template import Template
from native import NativeType, NativeField, NativeParameter, NativeFunction, NativeClass
from objc_file_parser import *
import utils

objc_types = ["NSInteger", "CGFloat", "NSString*"]
objc_types_length = len(objc_types)
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

function_prev_words = ["with", "did", "check", "change", "set", "init", "initWith"]
function_prev_words_lenth = len(function_prev_words)
function_main_words = ["Size", "Color", "Range", "Radius", "Scale", "Center", "Width", "Height", "Framebuffer",
                       "Duration",
                       "Average", "Processing", "Finished", "Block", "Options", "With", "And"]
function_main_words_lenth = len(function_main_words)


class ObjCFile:
    def __init__(self, config):
        self.config = config

        self.head_file_path = config["head_file"]
        self.source_file_path = config["source_file"]
        self.tpl_folder_path = config["tpl_folder"]
        if "search_path" in config:
            self.search_path = config["search_path"]
        else:
            self.search_path = ""

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

        self.generated_methods = []
        self.generated_fields = []

        self.native_class = None
        self.head_fp = None
        self.source_fp = None

        self.headers = []
        self.h_headers = []
        self.m_headers = []

    @staticmethod
    def generate_rule_name(random_prev_length=3, random_end_length=3, max_word=5, prev_probability=10):
        name = utils.generate_name_first_upper(random_prev_length, random_prev_length)
        if random.randint(0, 100) < prev_probability:
            name += name_prev_words[random.randint(0, name_prev_words_lenth - 1)]

        word_count = random.randint(1, max_word)
        for _ in range(word_count):
            name += name_main_words[random.randint(0, name_main_words_lenth - 1)]

        name += utils.generate_name_first_upper(random_end_length, random_end_length)
        return name

    @staticmethod
    def generate_field_name(random_prev_length=3, random_end_length=3, max_word=5, prev_probability=10,
                            auto_add_prev_probability=20):
        name = ""
        if random.randint(0, 100) < prev_probability:
            name += field_prev_words[random.randint(0, field_prev_words_lenth - 1)]
        elif random_prev_length > 0 and random.randint(0, 100) < auto_add_prev_probability:
            name += utils.generate_name_first_lower(random_prev_length, random_prev_length)

        word_count = random.randint(1, max_word)
        indexs = range(field_main_words_lenth)

        for i in range(word_count):
            indx = random.randint(0, field_main_words_lenth - 1 - i)
            name += field_main_words[indexs[indx]]
            indexs[indx] = indexs[-1 - i]

        if random_end_length > 0:
            name += utils.generate_name_first_upper(random_end_length, random_end_length)

        return name[0].lower() + name[1:]

    @staticmethod
    def generate_function_name(random_prev_length=3, random_end_length=3, max_word=5, prev_probability=10,
                               auto_add_prev_probability=80):
        name = ""
        if random.randint(0, 100) < prev_probability:
            name += function_prev_words[random.randint(0, function_prev_words_lenth - 1)]
        elif random_prev_length > 0 and random.randint(0, 100) < auto_add_prev_probability:
            name += utils.generate_name_first_lower(random_prev_length, random_prev_length)

        word_count = random.randint(1, max_word)

        indexs = range(function_main_words_lenth)

        for i in range(word_count):
            indx = random.randint(0, function_main_words_lenth - 1 - i)
            name += function_main_words[indexs[indx]]
            indexs[indx] = indexs[-1 - i]

        if random_end_length > 0:
            name += utils.generate_name_first_upper(random_end_length, random_end_length)
        return name[0].lower() + name[1:]

    @staticmethod
    def generate_type():
        return objc_types[random.randint(0, objc_types_length - 1)]

    @staticmethod
    def generate_value(type_name):
        if type_name == "NSInteger" or type_name == "int" or type_name == "long long":
            return str(utils.generate_int())
        elif type_name == "CGFloat" or type_name == "float" or type_name == "double":
            return str(utils.generate_float()) + "f"
        else:
            return "@\"%s\"" % utils.generate_string()

    @staticmethod
    def get_random_value(type_name):
        if type_name == "NSInteger" or type_name == "int" or type_name == "long long":
            return utils.generate_int()
        elif type_name == "CGFloat" or type_name == "float" or type_name == "double":
            return utils.generate_float()
        else:
            return utils.generate_string()

    @staticmethod
    def generate_field(tpl_folder_path):
        field_name = ObjCFile.generate_field_name(2, 3)
        field_type = NativeType(ObjCFile.generate_type())
        head_tpl_file = os.path.join(tpl_folder_path, "field.h")
        source_tpl_file = os.path.join(tpl_folder_path, "field.mm")
        return NativeField(field_name, field_type, head_tpl_file, source_tpl_file)

    @staticmethod
    def generate_parameter():
        param_name = ObjCFile.generate_function_name(0, 0)
        param_type = NativeType(ObjCFile.generate_type())
        return NativeParameter(param_name, param_type)

    @staticmethod
    def generate_function(tpl_folder_path, max_parameter_count=0):
        method_name = ObjCFile.generate_function_name(0, 2, 3, 50)
        parameters = []
        if max_parameter_count > 0:
            parameter_count = random.randint(0, max_parameter_count)
            for i in range(parameter_count):
                parameter = ObjCFile.generate_parameter()
                parameters.append(parameter)
        return_type = NativeType(None)
        # 30% create return type
        if random.randint(0, 10) > 7:
            return_type = NativeType(ObjCFile.generate_type())

        head_tpl_file = os.path.join(tpl_folder_path, "function.h")
        source_tpl_file = os.path.join(tpl_folder_path, "function.mm")
        return NativeFunction(method_name, parameters, return_type, head_tpl_file, source_tpl_file)

    def prepare(self):
        # check class name
        if not self.class_name:
            self.class_name = ObjCFile.generate_rule_name(3, 2)
            self.class_name = self.class_name[0].upper() + self.class_name[1:]

        # gen fields
        fields = None
        if "generate_field" in self.config:
            fields = []
            for i in range(self.config["generate_field"]):
                fields.append(self.generate_field(self.tpl_folder_path))

        # gen mthod
        methods = None
        if "generate_method" in self.config:
            methods = []
            if "max_parameter" in self.config:
                max_parameter = self.config["max_parameter"]
            else:
                max_parameter = 1

            for i in range(self.config["generate_method"]):
                methods.append(self.generate_function(self.tpl_folder_path, max_parameter))

        if "call_others" in self.config and self.config["call_others"]:
            for i in range(len(methods) - 1):
                methods[i].call_other(methods[i + 1])

        head_head_tpl_file = os.path.join(self.tpl_folder_path, "class_head.h")
        head_foot_tpl_file = os.path.join(self.tpl_folder_path, "class_foot.h")
        source_head_tpl_file = os.path.join(self.tpl_folder_path, "class_head.mm")
        source_foot_tpl_file = os.path.join(self.tpl_folder_path, "class_foot.mm")

        self.native_class = NativeClass(self.class_name, self.namespace, self, fields, methods,
                                        head_head_tpl_file, head_foot_tpl_file, source_head_tpl_file,
                                        source_foot_tpl_file)

    def generate_code(self):
        self.head_fp = open(self.head_file_path, "w+")
        self.source_fp = open(self.source_file_path, "w+")
        # gen head
        layout_h = Template(file=os.path.join(self.tpl_folder_path, "layout_head.h"),
                            searchList=[self])

        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_head.mm"),
                            searchList=[self])

        self.head_fp.write(str(layout_h))
        self.source_fp.write(str(layout_c))
        # gen body

        self.native_class.generate_code(self)

        # gen foot
        layout_h = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.h"),
                            searchList=[self])
        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.mm"),
                            searchList=[self])
        self.head_fp.write(str(layout_h))
        self.source_fp.write(str(layout_c))

        self.head_fp.close()
        self.source_fp.close()

    def to_string(self):
        head_str = ""
        source_str = ""

        # gen head
        layout_h = Template(file=os.path.join(self.tpl_folder_path, "layout_head.h"),
                            searchList=[self])

        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_head.mm"),
                            searchList=[self])

        head_str += str(layout_h)
        source_str += str(layout_c)
        # gen body

        class_head_str, class_source_str = self.native_class.to_string(self)
        head_str += class_head_str
        source_str += class_source_str
        # gen foot
        layout_h = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.h"),
                            searchList=[self])
        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.mm"),
                            searchList=[self])
        head_str += str(layout_h)
        source_str += str(layout_c)

        return head_str, source_str

    def get_class_execute_chain(self, class_index):
        return self.native_class.get_function_call_code(self.native_class.methods[0], self, class_index)

    def get_random_parameter_prev(self):
        return objc_method_parameter_prevs[random.randint(0, objc_method_parameter_prevs_length - 1)]


class ObjCFileInject(ObjCFile):
    def __init__(self, config):
        ObjCFile.__init__(self, config)

    def get_insert_class(self, classes):

        max_size = 0
        insert_class = None
        for class_info in classes:
            current_size = class_info.end_line - class_info.start_line
            if current_size > max_size:
                max_size = current_size
                insert_class = class_info
        return insert_class

    def get_source_insert_position(self, class_info, source_namespaces):
        if len(source_namespaces) > 0:
            for namespace_info in source_namespaces:
                if class_info.namespace == namespace_info.name:
                    return namespace_info.end_line
        return -1

    def get_include_position(self, lines):

        head_id_macro = None
        for i in range(0, len(lines)):
            line = lines[i].strip()
            if line.startswith("#ifndef"):
                head_id_macro = line[len("#ifndef"):].strip()
            elif line.startswith("#define") and head_id_macro == line[len("#define"):].strip():
                return i + 1
        return -1

    def _get_method_injects(self, source_file_parser, lines):
        inserts = {}

        inject_method_config = None
        if "inject_method" in self.config:
            inject_method_config = self.config["inject_method"]
        else:
            return inserts

        if "min_val" in inject_method_config:
            min_val = inject_method_config["min_val"]
        else:
            min_val = 1

        if "max_val" in inject_method_config:
            max_val = inject_method_config["max_val"]
        else:
            max_val = 5

        if "probability" in inject_method_config:
            probability = inject_method_config["probability"]
        else:
            probability = 30

        class_rule = None
        if "class_rule" in inject_method_config:
            class_rule = inject_method_config["class_rule"]

        method_rule = None
        if "method_rule" in inject_method_config:
            method_rule = inject_method_config["method_rule"]

        for method_info in source_file_parser.methods:
            # check probability
            need_inject = random.randint(0, 100) <= probability
            # print("pro:%d" % probability)
            if need_inject:
                # check rule
                need_inject = (not class_rule or not method_info.class_name or class_rule.test(
                    method_info.class_name)) and (not method_rule or method_rule.test(method_info.name))
                # print("test method:%s,%s" % (method_info.name, method_rule))
                if need_inject:

                    enable_positions = source_file_parser.get_method_inject_positions(method_info, lines)
                    if enable_positions and len(enable_positions):
                        pos = enable_positions[random.randrange(0, len(enable_positions))]

                        vals = []
                        val_count = random.randint(min_val, max_val)
                        for i in range(val_count):
                            val_type = ObjCFile.generate_type()
                            vals.append(ObjCFile.get_random_value(val_type))

                        code_tpl = Template(file=os.path.join(self.tpl_folder_path, "code_print.mm"),
                                            searchList=[
                                                {"line_index": pos, "vals": vals, "tag": utils.generate_string()}])
                        inserts[pos] = str(code_tpl)

        return inserts

    def inject_method(self):
        fp = open(self.source_file_path, "r+")
        source_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        source_file_parser = ObjCSourceFileParser(macros)
        source_file_parser.parse(source_lines)
        inserts = self._get_method_injects(source_file_parser, source_lines)

        if len(inserts) > 0:
            insert_positions = inserts.keys()

            insert_positions.sort(reverse=True)

            for pos in insert_positions:
                source_lines.insert(pos, inserts[pos])

            fp = open(self.source_file_path, "w+")
            fp.writelines(source_lines)
            fp.close()

    '''
    add field and method to class
    add garbage code to exists function(make sure garbage code not optimize by compiler)
    '''

    def inject_class(self):
        # check class info
        fp = open(self.head_file_path, "r+")
        head_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        head_file_parser = ObjCHeadFileParser(macros)
        head_file_parser.parse(head_lines)

        if len(head_file_parser.classes) > 0:
            # get first class
            class_info = self.get_insert_class(head_file_parser.classes)
            class_name = class_info.name
            class_end_line = class_info.end_line
            print("get class %s from %d to %d" % (class_info.name, class_info.start_line, class_info.end_line))
        else:
            print("no class find ")
            return

        self.native_class.class_name = class_name

        # check have source implement
        fp = open(self.source_file_path, "r+")
        source_lines = fp.readlines()
        fp.close()

        source_file_parser = ObjCSourceFileParser(macros)
        source_file_parser.parse(source_lines)

        source_insert_line = self.get_source_insert_position(class_info, source_file_parser.namespaces)

        if source_insert_line == -1:
            print("can't find namespace for %s,%s" % (class_info.name, class_info.namespace))
            # no in source,add implement in head
            for method in self.native_class.methods:
                method.head_tpl_file = os.path.join(self.tpl_folder_path, "function_with_impl.h")

        head_str, source_str = self.native_class.get_generated_field_method(self)

        # insert header
        head_lines.insert(class_end_line, head_str)
        # this is before the head declare
        head_lines.insert(class_end_line, "public:\n")

        # insert include <string> to head
        insert_include_pos = self.get_include_position(head_lines)
        if insert_include_pos > -1:
            head_lines.insert(insert_include_pos, "\n#include <string>\n")

        fp = open(self.head_file_path, "w+")
        fp.writelines(head_lines)
        fp.close()

        # inject code to method
        #  check method inject position

        # insert source
        if source_insert_line > -1:
            source_lines.insert(source_insert_line, source_str)

            fp = open(self.source_file_path, "w+")
            fp.writelines(source_lines)
            fp.close()

    def inject_class_just_head(self):
        # check class info
        fp = open(self.head_file_path, "r+")
        head_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        head_file_parser = ObjCHeadFileParser(macros)
        head_file_parser.parse(head_lines)

        if len(head_file_parser.classes) > 0:
            # get first class
            class_info = self.get_insert_class(head_file_parser.classes)
            class_name = class_info.name
            class_end_line = class_info.end_line
            print("get class %s from %d to %d" % (class_info.name, class_info.start_line, class_info.end_line))
        else:
            print("no class find ")
            return

        self.native_class.class_name = class_name

        for method in self.native_class.methods:
            method.head_tpl_file = os.path.join(self.tpl_folder_path, "function_with_impl.h")

        head_str, content_str = self.native_class.get_generated_field_method(self)

        # insert header
        head_lines.insert(class_end_line, head_str)
        # this is before the head declare
        head_lines.insert(class_end_line, "public:\n")

        # insert include <string> to head
        insert_include_pos = self.get_include_position(head_lines)
        if insert_include_pos > -1:
            head_lines.insert(insert_include_pos, "\n#include <string>\n")

        fp = open(self.head_file_path, "w+")
        fp.writelines(head_lines)
        fp.close()

    def inject_code(self):
        # check class info
        fp = open(self.head_file_path, "r+")
        head_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        head_file_parser = ObjCHeadFileParser(macros)
        head_file_parser.parse(head_lines)

        if len(head_file_parser.classes) > 0:
            # get first class
            class_info = self.get_insert_class(head_file_parser.classes)
            class_name = class_info.name
            class_end_line = class_info.end_line
            print("get class %s from %d to %d" % (class_info.name, class_info.start_line, class_info.end_line))
        else:
            print("no class find ")
            return

        self.native_class.class_name = class_name

        # check have source implement
        fp = open(self.source_file_path, "r+")
        source_lines = fp.readlines()
        fp.close()

        source_file_parser = ObjCSourceFileParser(macros)
        source_file_parser.parse(source_lines)

        source_insert_line = self.get_source_insert_position(class_info, source_file_parser.namespaces)

        if source_insert_line == -1:
            print("can't find namespace for %s,%s" % (class_info.name, class_info.namespace))
            # no in source,add implement in head
            for method in self.native_class.methods:
                method.head_tpl_file = os.path.join(self.tpl_folder_path, "function_with_impl.h")

        head_str, source_str = self.native_class.get_generated_field_method(self)

        # insert header
        head_lines.insert(class_end_line, head_str)
        # this is before the head declare
        head_lines.insert(class_end_line, "public:\n")

        # insert include <string> to head
        insert_include_pos = self.get_include_position(head_lines)
        if insert_include_pos > -1:
            head_lines.insert(insert_include_pos, "\n#include <string>\n")

        fp = open(self.head_file_path, "w+")
        fp.writelines(head_lines)
        fp.close()

        # inject code to method
        #  check method inject position
        inserts = self._get_method_injects(source_file_parser, source_lines)

        # insert source
        if source_insert_line > -1:
            inserts[source_insert_line] = source_str

        if len(inserts) > 0:
            insert_positions = inserts.keys()

            insert_positions.sort(reverse=True)

            for pos in insert_positions:
                source_lines.insert(pos, inserts[pos])

            fp = open(self.source_file_path, "w+")
            fp.writelines(source_lines)
            fp.close()
