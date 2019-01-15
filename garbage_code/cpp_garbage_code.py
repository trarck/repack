# -*- coding: utf-8 -*-
import os
import random

from pbxproj import XcodeProject
from Cheetah.Template import Template
from native import NativeType, NativeField, NativeParameter, NativeFunction, NativeClass
from generater import RandomGenerater

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
                                                {"line_index": pos, "vals": vals,
                                                 "tag": RandomGenerater.generate_string()}])
                        inserts[pos] = str(code_tpl)

        return inserts


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
