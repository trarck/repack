# -*- coding: utf-8 -*-
import os
import random

from pbxproj import XcodeProject
from Cheetah.Template import Template
from native import NativeType, NativeField, NativeParameter, NativeFunction, NativeClass
import utils

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

        self.native_class = None
        self.head_fp = None
        self.source_fp = None
        self.hpp_headers = []
        self.cpp_headers = []
        self.headers = []

    @staticmethod
    def generate_type():
        return cpp_types[random.randint(0, cpp_types_length - 1)]

    @staticmethod
    def generate_value(type_name):
        if type_name == "int" or type_name == "long long":
            return str(utils.generate_int())
        elif type_name == "float" or type_name == "double":
            return str(utils.generate_float()) + "f"
        else:
            return "\"%s\"" % utils.generate_string()

    @staticmethod
    def generate_field(tpl_folder_path):
        field_name = utils.generate_name()
        field_type = NativeType(CppFile.generate_type())
        head_tpl_file = os.path.join(tpl_folder_path, "field.h")
        source_tpl_file = os.path.join(tpl_folder_path, "field.cpp")
        return NativeField(field_name, field_type, head_tpl_file, source_tpl_file)

    @staticmethod
    def generate_parameter():
        param_name = utils.generate_name()
        param_type = NativeType(CppFile.generate_type())
        return NativeParameter(param_name, param_type)

    @staticmethod
    def generate_function(tpl_folder_path, max_parameter_count=0):
        method_name = utils.generate_name()
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
            self.class_name = utils.generate_name(8, 32)
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

    def get_head_class_define_position(self, lines):
        start_line = -1
        end_line = -1
        line_index = 0

        find_start = -1
        find_end = -1
        current_class_line_count = 0

        # get max class start end
        for line in lines:
            if line.startswith("class"):
                start_line = line_index
            if line.startswith("};"):
                end_line = line_index
                line_count = end_line - start_line
                if line_count > current_class_line_count:
                    current_class_line_count = line_count
                    find_start = start_line
                    find_end = end_line
            line_index += 1

        return find_start, find_end

    def get_source_first_impl_position(self, class_name, lines):
        line_index = 0
        impl = "%s::" % class_name
        for line in lines:
            if line.find(impl):
                return line_index
            line_index += 1
        return -1

    def get_source_last_impl_position(self, class_name, lines):
        find_position = -1
        line_index = 0
        impl = "%s::" % class_name
        for line in lines:
            if line.find(impl) > -1:
                find_position = line_index
            line_index += 1
        return find_position

    def get_class_name(self, line):
        if line.startswith("class"):
            parent_position = line.find(":")
            if parent_position > 0:
                class_define = line[5:parent_position].strip()
            else:
                b_position = line.find("{")
                if b_position > 0:
                    class_define = line[5:b_position].strip()
                else:
                    class_define = line[5:].strip()
            cs = class_define.split(" ")
            return cs[-1]
        return None

    def inject_code(self):
        # check class info
        fp = open(self.head_file_path, "r+")
        lines = fp.readlines()
        fp.close()

        class_define_line, end_line = self.get_head_class_define_position(lines)
        class_name = self.get_class_name(lines[class_define_line])
        print("get class %s from %d to %d" % (class_name, class_define_line, end_line))
        self.native_class.class_name = class_name

        head_str, source_str = self.native_class.get_generated_field_method(self)

        # insert header
        lines.insert(end_line, head_str)
        # this is before the head declare
        lines.insert(end_line, "public:\n")

        fp = open(self.head_file_path, "w+")
        fp.writelines(lines)
        fp.close()

        # insert source
        fp = open(self.source_file_path, "r+")
        lines = fp.readlines()
        fp.close()
        end_line = self.get_source_last_impl_position(class_name, lines)
        lines.insert(end_line, source_str)
        fp = open(self.source_file_path, "w+")
        fp.writelines(lines)
        fp.close()


class CppGarbageCode:
    def __init__(self, tpl_folder_path):
        self.tpl_folder_path = tpl_folder_path.encode("utf-8")
        self.generate_config = None
        self.inject_config = None
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
            group_name = utils.generate_string(6, 10)

        call_others = True
        if "call_others" in self.generate_config:
            call_others = self.generate_config["call_others"]

        generated_files = []
        generated_head_files = []

        namespace = utils.generate_name(5, 8).lower()

        call_generate_codes = []

        class_index = 1
        for i in range(gen_file_count):
            class_name = utils.generate_name_first_upper(8, 16)
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
                                 searchList=[{"code": "".join(call_generate_codes)}])
        exec_once = str(exec_once_tpl)

        if "generate_executor" in generate_config and generate_config["generate_executor"]:
            print("generate a executor")
        else:
            print("insert into execute file")
            include_heads = "\n"
            for head_file in generated_head_files:
                include_heads += "#include \"%s\"\n" % head_file

        # create action execute in repack
        insert_head_action = {
            "operation": "insert",
            "file_path": exec_code_file_path,
            "keys": generate_config["include_insert_keys"],
            "words": include_heads
        }
        insert_code_action = {
            "operation": "insert",
            "file_path": exec_code_file_path,
            "keys": generate_config["code_insert_keys"],
            "words": exec_once
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
        if file_path_without_ext in self._injected_files:
            return False
        self._injected_files[file_path_without_ext] = True

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
                generate_field_count = self._parse_range_count("generate_field_count", self.inject_config)
                generate_method_count = self._parse_range_count("generate_method_count", self.inject_config)
                parameter_count = self._parse_range_count("parameter_count", self.inject_config)

                a_file_inject_config = self.inject_config.copy()
                a_file_inject_config["head_file"] = head_file_path
                a_file_inject_config["source_file"] = source_file_path
                call_others = True

                if "call_others" in self.inject_config:
                    call_others = self.inject_config["call_others"]

                cpp_inject = CppFileInject({
                    "head_file": head_file_path,
                    "source_file": source_file_path,
                    "tpl_folder": self.tpl_folder_path,
                    "generate_field": generate_field_count,
                    "generate_method": generate_method_count,
                    "max_parameter": parameter_count,
                    "call_others": call_others
                })
                cpp_inject.prepare()
                cpp_inject.inject_code()
                return True
            else:
                print("===>cpp code inject source file or head file not exists of %s" % file_path_without_ext)
        else:
            print("===>cpp code inject skip %s" % file_path)
        return False

    def _inject_dir(self, folder_path, include_rules=None):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isdir(file_path):
                self._inject_dir(file_path, include_rules)
            elif os.path.isfile(file_path):
                if utils.in_rules(file_path, include_rules):
                    self._inject_file(file_path)

    def inject_files(self, files, inject_config):
        self.inject_config = inject_config
        if "include" in self.inject_config:
            include_rules = self.inject_config["include"]
        else:
            include_rules = "*.h"
        self._injected_files = {}
        include_rules = utils.convert_rules(include_rules)
        for file_path in files:
            if os.path.isdir(file_path):
                self._inject_dir(file_path, include_rules)
            elif os.path.isfile(file_path):
                # config file force inject
                self._inject_file(file_path, True)
