# -*- coding: utf-8 -*-
import os
import random

from pbxproj import XcodeProject
from Cheetah.Template import Template
from native import NativeType, NativeField, NativeParameter, NativeFunction, NativeClass
from cpp_file_parser import *
from generater import RandomGenerater
import gc_utils

cpp_types = ["int", "long long", "float", "double", "std::string"]
cpp_types_length = len(cpp_types)


class CppFile:
    def __init__(self, config):
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
        self.config = config

        self.generated_methods = []
        self.generated_fields = []
        self.headers = []
        self.hpp_headers = []
        self.cpp_headers = []

        self.native_class = None
        self.head_fp = None
        self.source_fp = None

    @staticmethod
    def generate_type():
        return cpp_types[random.randint(0, cpp_types_length - 1)]

    @staticmethod
    def generate_value(type_name):
        if type_name == "int" or type_name == "long long":
            return str(RandomGenerater.generate_int())
        elif type_name == "float" or type_name == "double":
            return str(RandomGenerater.generate_float()) + "f"
        else:
            return "\"%s\"" % RandomGenerater.generate_string()

    @staticmethod
    def get_random_value(type_name):
        if type_name == "int" or type_name == "long long":
            return RandomGenerater.generate_int()
        elif type_name == "float" or type_name == "double":
            return RandomGenerater.generate_float()
        else:
            return RandomGenerater.generate_string()

    @staticmethod
    def generate_field(tpl_folder_path):
        field_name = RandomGenerater.generate_string()
        field_type = NativeType(CppFile.generate_type())
        head_tpl_file = os.path.join(tpl_folder_path, "field.h")
        source_tpl_file = os.path.join(tpl_folder_path, "field.cpp")
        return NativeField(field_name, field_type, head_tpl_file, source_tpl_file)

    @staticmethod
    def generate_parameter():
        param_name = RandomGenerater.generate_string()
        param_type = NativeType(CppFile.generate_type())
        return NativeParameter(param_name, param_type)

    @staticmethod
    def generate_function(tpl_folder_path, max_parameter_count=0):
        method_name = RandomGenerater.generate_string()
        parameters = []
        if max_parameter_count > 0:
            parameter_count = random.randint(0, max_parameter_count)
            for i in range(parameter_count):
                parameter = CppFile.generate_parameter()
                parameters.append(parameter)
        return_type = NativeType(None)
        # 30% create return type
        if random.randint(0, 10) > 7:
            return_type = NativeType(CppFile.generate_type())

        head_tpl_file = os.path.join(tpl_folder_path, "function.h")
        source_tpl_file = os.path.join(tpl_folder_path, "function.cpp")
        return NativeFunction(method_name, parameters, return_type, head_tpl_file, source_tpl_file)

    def prepare(self):
        # check class name
        if not self.class_name:
            self.class_name = RandomGenerater.generate_string(8, 32)
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
        source_head_tpl_file = os.path.join(self.tpl_folder_path, "class_head.cpp")
        source_foot_tpl_file = os.path.join(self.tpl_folder_path, "class_foot.cpp")

        self.native_class = NativeClass(self.class_name, self.namespace, self, fields, methods,
                                        head_head_tpl_file, head_foot_tpl_file, source_head_tpl_file,
                                        source_foot_tpl_file)

    def generate_code(self):
        self.head_fp = open(self.head_file_path, "w+")
        self.source_fp = open(self.source_file_path, "w+")
        # gen head
        layout_h = Template(file=os.path.join(self.tpl_folder_path, "layout_head.h"),
                            searchList=[self])

        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_head.cpp"),
                            searchList=[self])

        self.head_fp.write(str(layout_h))
        self.source_fp.write(str(layout_c))
        # gen body

        self.native_class.generate_code(self)

        # gen foot
        layout_h = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.h"),
                            searchList=[self])
        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.cpp"),
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

        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_head.cpp"),
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
        layout_c = Template(file=os.path.join(self.tpl_folder_path, "layout_foot.cpp"),
                            searchList=[self])
        head_str += str(layout_h)
        source_str += str(layout_c)

        return head_str, source_str

    def get_class_execute_chain(self, class_index):
        return self.native_class.get_function_call_code(self.native_class.methods[0], self, class_index)


class CppFileInject(CppFile):
    def __init__(self, config):
        CppFile.__init__(self, config)

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
        print(inject_method_config)
        for method_info in source_file_parser.methods:
            # check probability
            need_inject = random.randint(0, 100) <= probability
            print("pro:%d" % probability)
            if need_inject:
                # check rule
                need_inject = (not class_rule or not method_info.class_name or class_rule.test(
                    method_info.class_name)) and (not method_rule or method_rule.test(method_info.name))
                print("test method:%s,%s" % (method_info.name, method_rule))
                if need_inject:

                    enable_positions = source_file_parser.get_method_inject_positions(method_info, lines)
                    if enable_positions and len(enable_positions):
                        pos = enable_positions[random.randrange(0, len(enable_positions))]

                        vals = []
                        val_count = random.randint(min_val, max_val)
                        for i in range(val_count):
                            val_type = CppFile.generate_type()
                            vals.append(CppFile.get_random_value(val_type))

                        code_tpl = Template(file=os.path.join(self.tpl_folder_path, "code_print.cpp"),
                                            searchList=[
                                                {"line_index": pos, "vals": vals, "tag": RandomGenerater.generate_string()}])
                        inserts[pos] = str(code_tpl)

        return inserts

    def inject_method(self):
        fp = open(self.source_file_path, "rU")
        source_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        source_file_parser = CppSourceFileParser(macros)
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
        fp = open(self.head_file_path, "rU")
        head_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        head_file_parser = CppHeadFileParser(macros)
        head_file_parser.parse(head_lines)

        if len(head_file_parser.classes) > 0:
            # get first class
            class_info = self.get_insert_class(head_file_parser.classes)
            if class_info:
                class_name = class_info.name
                class_end_line = class_info.end_line
                print("get class %s from %d to %d" % (class_info.name, class_info.start_line, class_info.end_line))
            else:
                print("no class find ")
                return
        else:
            print("no class find ")
            return

        self.native_class.class_name = class_name

        # check have source implement
        fp = open(self.source_file_path, "rU")
        source_lines = fp.readlines()
        fp.close()

        source_file_parser = CppSourceFileParser(macros)
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
        fp = open(self.head_file_path, "rU")
        head_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        head_file_parser = CppHeadFileParser(macros)
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
        fp = open(self.head_file_path, "rU")
        head_lines = fp.readlines()
        fp.close()

        macros = None
        if "macros" in self.config:
            macros = self.config["macros"]
        head_file_parser = CppHeadFileParser(macros)
        head_file_parser.parse(head_lines)

        if len(head_file_parser.classes) > 0:
            # get first class
            class_info = self.get_insert_class(head_file_parser.classes)
            if class_info:
                class_name = class_info.name
                class_end_line = class_info.end_line
                print("get class %s from %d to %d" % (class_info.name, class_info.start_line, class_info.end_line))
            else:
                print("no class find ")
                return
        else:
            print("no class find ")
            return

        self.native_class.class_name = class_name

        # check have source implement
        fp = open(self.source_file_path, "rU")
        source_lines = fp.readlines()
        fp.close()

        source_file_parser = CppSourceFileParser(macros)
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


class CppGarbageCode:
    def __init__(self, tpl_folder_path):
        self.tpl_folder_path = tpl_folder_path.encode("utf-8")
        self.generate_config = None
        self.inject_config = None
        self._inject_checked_files = None
        self._injected_files = None

    def _parse_range_count(self, name, config, default_min=1):
        if name in config:
            return config[name]

        max_key = "max_" + name
        min_key = "min_" + name

        if max_key in config:
            max_value = config[max_key]

        if min_key in config:
            min_value = config[min_key]
        else:
            min_value = default_min

        if min_value > max_value:
            max_value = min_value
        return random.randint(min_value, max_value)

    def _get_xcode_project_file_path(self, project_dir):
        if project_dir.find(".xcodeproj") > -1:
            return project_dir

        files = os.listdir(project_dir)
        for filename in files:
            if filename.find(".xcodeproj") > -1:
                return os.path.join(project_dir, filename)
        return None

    def generate_cpp_file(self, out_folder_path, xcode_project_path, exec_code_file_path, generate_config):
        self.generate_config = generate_config

        gen_file_count = self._parse_range_count("generate_file_count", generate_config, 6)
        generate_field_count = self._parse_range_count("generate_field_count", generate_config)
        generate_method_count = self._parse_range_count("generate_method_count", generate_config)
        parameter_count = self._parse_range_count("parameter_count", generate_config)

        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

        if "group_name" in self.generate_config:
            group_name = self.generate_config["group_name"]
        else:
            group_name = RandomGenerater.generate_string(6, 10)

        call_others = True
        if "call_others" in self.generate_config:
            call_others = self.generate_config["call_others"]

        generated_files = []
        generated_head_files = []

        namespace = RandomGenerater.generate_string(5, 8).lower()

        call_generate_codes = []

        class_index = 1
        for i in range(gen_file_count):
            class_name = RandomGenerater.generate_string_first_upper(8, 16)
            head_file_name = os.path.join(out_folder_path, class_name + ".h")
            source_file_name = os.path.join(out_folder_path, class_name + ".cpp")
            generated_files.append(head_file_name)
            generated_files.append(source_file_name)
            generated_head_files.append(class_name + ".h")

            generator = CppFile({
                "head_file": head_file_name,
                "source_file": source_file_name,
                "tpl_folder": self.tpl_folder_path,
                "class_name": class_name,
                "namespace": namespace,
                "generate_field": generate_field_count,
                "generate_method": generate_method_count,
                "max_parameter": parameter_count,
                "call_others": call_others
            })
            generator.prepare()
            generator.generate_code()
            call_generate_func = generator.get_class_execute_chain(class_index)
            call_generate_codes.append(call_generate_func)
            class_index += 1

        # generate call generated code prevent delete by link optimization
        exec_once_tpl = Template(file=os.path.join(self.tpl_folder_path, "exec_code_once.cpp"),
                                 searchList=[{"code": "".join(call_generate_codes),
                                              "prefix": RandomGenerater.generate_string()}])
        exec_once = str(exec_once_tpl)

        if "generate_executor" in generate_config and generate_config["generate_executor"]:
            print("generate a executor")
        else:
            print("insert into execute file")
            include_heads = "\n"
            for head_file in generated_head_files:
                include_heads += "#include \"%s\"\n" % head_file

        auto_all_name = RandomGenerater.generate_string(20, 30)
        auto_all_function = RandomGenerater.generate_string(20, 30)
        auto_all_head_file = os.path.join(out_folder_path, auto_all_name + ".h")
        auto_all_source_file = os.path.join(out_folder_path, auto_all_name + ".cpp")
        generated_files.append(auto_all_head_file)
        generated_files.append(auto_all_source_file)

        auto_all_head_tpl = Template(file=os.path.join(self.tpl_folder_path, "auto_all.h"),
                                     searchList=[{"name": auto_all_name, "headers": include_heads,
                                                  "auto_all_function": auto_all_function}])

        auto_all_source_tpl = Template(file=os.path.join(self.tpl_folder_path, "auto_all.cpp"),
                                       searchList=[{"name": auto_all_name, "code": exec_once,
                                                    "auto_all_function": auto_all_function}])

        fp = open(auto_all_head_file, "w+")
        fp.write(str(auto_all_head_tpl))
        fp.close()

        fp = open(auto_all_source_file, "w+")
        fp.write(str(auto_all_source_tpl))
        fp.close()

        # create action execute in repack
        insert_head_action = {
            "operation": "insert",
            "file_path": exec_code_file_path,
            "keys": generate_config["include_insert_keys"],
            "words": "\n#include \"%s.h\"\n" % auto_all_name
        }
        insert_code_action = {
            "operation": "insert",
            "file_path": exec_code_file_path,
            "keys": generate_config["code_insert_keys"],
            "words": "\n%s();\n" % auto_all_function
        }
        modify_exec_code_actions = {
            "name": "modify_files",
            "files": [insert_head_action, insert_code_action]
        }

        # add generated files to xcode project

        pbx_proj_file_path = os.path.join(self._get_xcode_project_file_path(xcode_project_path), "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        # add out dir to head search path
        pbx_project.add_header_search_paths(out_folder_path)
        # add a group
        group = pbx_project.add_group(group_name)
        # add files
        for file_path in generated_files:
            pbx_project.add_file(file_path, group)
        pbx_project.save()

        return modify_exec_code_actions

    def _inject_file(self, file_path, force=False):
        file_path_without_ext = os.path.splitext(file_path)[0]
        if file_path_without_ext in self._inject_checked_files:
            return False
        self._inject_checked_files[file_path_without_ext] = True

        if not force:
            probability = self.inject_config["probability"]
            need_inject = random.randint(0, 100) <= probability
        else:
            need_inject = True

        if need_inject:
            head_file_path = file_path_without_ext + ".h"
            source_file_path = file_path_without_ext + ".cpp"
            if os.path.exists(head_file_path) and os.path.exists(source_file_path):
                print("===>cpp code inject basefile %s" % file_path_without_ext)
                self._injected_files.append(file_path_without_ext)
                generate_field_count = self._parse_range_count("generate_field_count", self.inject_config)
                generate_method_count = self._parse_range_count("generate_method_count", self.inject_config)
                parameter_count = self._parse_range_count("parameter_count", self.inject_config)

                a_file_inject_config = self.inject_config.copy()
                a_file_inject_config["head_file"] = head_file_path
                a_file_inject_config["source_file"] = source_file_path
                call_others = True
                if "call_others" in self.inject_config:
                    call_others = self.inject_config["call_others"]

                if "inject_method" in self.inject_config:
                    inject_method_config = self.inject_config["inject_method"]

                    if "include_class" in inject_method_config:
                        include_class_rules = inject_method_config["include_class"]
                    else:
                        include_class_rules = None

                    if "exclude_class" in inject_method_config:
                        exclude_class_rules = inject_method_config["exclude_class"]
                    else:
                        exclude_class_rules = None

                    if include_class_rules or exclude_class_rules:
                        class_rule = gc_utils.create_rules(include_class_rules, exclude_class_rules)
                        inject_method_config["class_rule"] = class_rule

                    if "include_method" in inject_method_config:
                        include_method_rules = inject_method_config["include_method"]
                    else:
                        include_method_rules = None

                    if "exclude_method" in inject_method_config:
                        exclude_method_rules = inject_method_config["exclude_method"]
                    else:
                        exclude_method_rules = None

                    if include_method_rules or exclude_method_rules:
                        method_rule = gc_utils.create_rules(include_method_rules, exclude_method_rules)
                        print(method_rule)
                        inject_method_config["method_rule"] = method_rule

                cpp_inject = CppFileInject({
                    "head_file": head_file_path,
                    "source_file": source_file_path,
                    "tpl_folder": self.tpl_folder_path,
                    "generate_field": generate_field_count,
                    "generate_method": generate_method_count,
                    "max_parameter": parameter_count,
                    "call_others": call_others,
                    "macros": self.inject_config["macros"],
                    "inject_method": inject_method_config
                })
                cpp_inject.prepare()
                cpp_inject.inject_code()
                # cpp_inject.inject_code_just_head()
                return True
            else:
                print("===>cpp code inject source file or head file not exists of %s" % file_path_without_ext)
        else:
            print("===>cpp code inject skip %s" % file_path)
        return False

    def _inject_dir(self, folder_path, rule=None):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isdir(file_path):
                self._inject_dir(file_path, rule)
            elif os.path.isfile(file_path):
                print("#Rule:%s=%s" % (file_path, str(rule.test(file_path))))
                if not rule or rule.test(file_path):
                    self._inject_file(file_path)

    def inject_files(self, files, inject_config):
        self.inject_config = inject_config
        if "include" in self.inject_config:
            include_rules = self.inject_config["include"]
        else:
            include_rules = ["*.h"]

        exclude_rules = None
        if "exclude" in self.inject_config:
            exclude_rules = self.inject_config["exclude"]

        rule = gc_utils.create_rules(include_rules, exclude_rules)

        self._inject_checked_files = {}
        self._injected_files = []

        for file_path in files:
            if os.path.isdir(file_path):
                self._inject_dir(file_path, rule)
            elif os.path.isfile(file_path):
                # config file force inject
                self._inject_file(file_path, True)

        print("inject %d files" % len(self._injected_files))
        for injected_file in self._injected_files:
            print("==> inject %s" % injected_file)
