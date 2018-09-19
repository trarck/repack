import os
import utils
import random

from pbxproj import XcodeProject, PBXProvioningTypes
from Cheetah.Template import Template

import utils

cpp_types = ["int", "long long", "float", "double", "std::string"]
cpp_types_length = len(cpp_types)


class NativeType:
    def __init__(self, name):
        self.name = name

    def to_string(self, generator):
        if self.name:
            return self.name
        else:
            return "void"


class NativeField:
    def __init__(self, name, field_type):
        self.name = name
        self.native_type = field_type

    def generate_code(self, current_class, generator):
        field_h = Template(file=os.path.join(generator.tpl_folder_path, "field.h"),
                           searchList=[current_class, self])

        field_c = Template(file=os.path.join(generator.tpl_folder_path, "field.cpp"),
                           searchList=[current_class, self])

        generator.head_fp.write(str(field_h))
        generator.source_fp.write(str(field_c))

    def to_string(self, current_class, generator):
        field_h = Template(file=os.path.join(generator.tpl_folder_path, "field.h"),
                           searchList=[current_class, self])

        field_c = Template(file=os.path.join(generator.tpl_folder_path, "field.cpp"),
                           searchList=[current_class, self])

        return str(field_h), str(field_c)


class NativeParameter:
    def __init__(self, name, param_type):
        self.name = name
        self.native_type = param_type

    def to_string(self, generator):
        return self.native_type.to_string(generator) + " " + self.name


class NativeFunction:
    def __init__(self, name, parameters, return_type):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.call_others = []

    def generate_code(self, current_class, generator):
        function_h = Template(file=os.path.join(generator.tpl_folder_path, "function.h"),
                              searchList=[current_class, self])

        function_c = Template(file=os.path.join(generator.tpl_folder_path, "function.cpp"),
                              searchList=[current_class, self])

        generator.head_fp.write(str(function_h))
        generator.source_fp.write(str(function_c))

    def to_string(self, current_class, generator):
        function_h = Template(file=os.path.join(generator.tpl_folder_path, "function.h"),
                              searchList=[current_class, self])

        function_c = Template(file=os.path.join(generator.tpl_folder_path, "function.cpp"),
                              searchList=[current_class, self])

        return str(function_h), str(function_c)

    def call_other(self, func):
        self.call_others.append(func)


class NativeClass:
    def __init__(self, name, namespace, generator, fields, methods):
        self.class_name = name
        self.namespace = namespace
        self.generator = generator
        self.fields = fields
        self.methods = methods

        self.namespace_begin = None
        self.namespace_end = None

    def prepare_namespace(self):
        if self.namespace:
            if isinstance(self.namespace, (str)):
                ns = self.namespace.split('.')
            else:
                ns = self.namespace
            self.namespace_begin = ""
            self.namespace_end = ""
            for name in ns:
                self.namespace_begin += "namespace %s {" % name
                self.namespace_end += "}"

    def generate_code(self, generator):
        self.prepare_namespace()
        # gen head
        class_h = Template(file=os.path.join(generator.tpl_folder_path, "class_head.h"),
                           searchList=[self])

        class_c = Template(file=os.path.join(generator.tpl_folder_path, "class_head.cpp"),
                           searchList=[self])

        generator.head_fp.write(str(class_h))
        generator.source_fp.write(str(class_c))

        # gen fileds
        for filed in self.fields:
            filed.generate_code(self, generator)

        for method in self.methods:
            method.generate_code(self, generator)

        # gen foot
        class_h = Template(file=os.path.join(generator.tpl_folder_path, "class_foot.h"),
                           searchList=[self])

        class_c = Template(file=os.path.join(generator.tpl_folder_path, "class_foot.cpp"),
                           searchList=[self])

        generator.head_fp.write(str(class_h))
        generator.source_fp.write(str(class_c))

    def to_generated_string(self, generator):
        head_str = ""
        source_str = ""
        # generated fileds
        for filed in self.fields:
            h_str, c_str = filed.to_string(self, generator)
            head_str += h_str
            source_str += c_str
        # generated methods
        for method in self.methods:
            h_str, c_str = method.to_string(self, generator)
            head_str += h_str
            source_str += c_str
        return head_str, source_str


class CppFile:
    def __init__(self, config):
        self.head_file_path = config["head_file"]
        self.source_file_path = config["source_file"]
        self.tpl_folder_path = config["tpl_folder"]
        if "search_path" in config:
            self.search_path = config["search_path"]

        self.class_name = None
        if "class_name" in config:
            class_name = config["file_path"]
            cs = class_name.split('.')
            self.class_name = cs[-1]
            del cs[-1]
            self.namespace = cs

        if "namespace" in config:
            self.namespace = config["namespace"]

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
    def generate_field():
        print("generate field")
        field_name = utils.generate_name()
        field_type = NativeType(CppFile.generate_type())
        return NativeField(field_name, field_type)

    @staticmethod
    def generate_parameter():
        print("generate field")
        param_name = utils.generate_name()
        param_type = NativeType(CppFile.generate_type())
        return NativeParameter(param_name, param_type)

    @staticmethod
    def generate_function(max_parameter_count=0):
        print("generate function")
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

        return NativeFunction(method_name, parameters, return_type)

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
                fields.append(self.generate_field())

        # gen mthod
        methods = None
        if "generate_method" in self.config:
            methods = []
            if "max_parameter" in self.config:
                max_parameter = self.config["max_parameter"]

            for i in range(self.config["generate_method"]):
                methods.append(self.generate_function(max_parameter))

        if "call_others" in self.config and self.config["call_others"]:
            for i in range(len(methods) - 1):
                methods[i].call_other(methods[i + 1])

        self.native_class = NativeClass(self.class_name, self.namespace, self, fields, methods)

    def generate_code(self):
        self.prepare()

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
            if line.find(impl):
                find_position = line_index
            line_index += 1
        return find_position

    def get_class_name(self, line):
        if line.startswith("class"):
            parent_position = line.find(":")
            if parent_position > 0:
                class_define = line[5:parent_position].strip()
            else:
                class_define = line[5:].strip()
            cs = class_define.split(" ")
            return cs[-1]
        return None

    def inject_code(self):
        self.prepare()
        head_str, source_str = self.native_class.to_generated_string(self)

        # insert head
        fp = open(self.head_file_path, "r+")
        lines = fp.readlines()
        fp.close()
        class_define_line, end_line = self.get_head_class_define_position(lines)
        class_name = self.get_class_name(lines[class_define_line])
        print("get class %s from %d to %d" % (class_name, class_define_line, end_line))

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
    def __init__(self,tpl_folder_path):
        self.tpl_folder_path=tpl_folder_path
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

    def generate_cpp_file(self, out_folder_path, xcode_project_file_path, generate_config):
        self.generate_config = generate_config

        gen_file_count = self._parse_range_count("generate_file_count",generate_config,6)
        generate_field_count=self._parse_range_count("generate_field_count",generate_config)
        generate_method_count = self._parse_range_count("generate_method_count", generate_config)
        parameter_count = self._parse_range_count("parameter_count", generate_config)

        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

        if "group_name" in self.generate_config:
            group_name = self.generate_config["group_name"]
        else:
            group_name = utils.generate_string(6, 10)

        generated_files = []
        namespace = utils.generate_name(5, 8).lower()

        for i in range(gen_file_count):
            class_name = utils.generate_name_first_upper(8, 16)
            head_file_name = os.path.join(out_folder_path, class_name + ".h")
            source_file_name = os.path.join(out_folder_path, class_name + ".cpp")
            generated_files.append(head_file_name)
            generated_files.append(source_file_name)
            generator = CppFile({
                "head_file": head_file_name,
                "source_file": source_file_name,
                "tpl_folder": self.tpl_folder_path,
                "namespace": namespace,
                "generate_field": generate_field_count,
                "generate_method":generate_method_count,
                "max_parameter": parameter_count,
                "call_others": self.generate_config["call_others"]
            })
            generator.generate_code()
        # add generated files to xcode project
        pbx_proj_file_path = os.path.join(xcode_project_file_path, "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        # add out dir to head search path
        pbx_project.add_header_search_paths(out_folder_path)
        # add a group
        group = pbx_project.add_group(group_name)
        # add files
        for file_path in generated_files:
            pbx_project.add_file(file_path, group)
        pbx_project.save()

    def _inject_file(self, file_path, force=False):
        file_path_without_ext = os.path.splitext(file_path)[0]
        if file_path_without_ext in self._injected_files:
            return False
        self._injected_files[file_path_without_ext] = True

        if not force:
            probability = self.inject_config["probability"]
            need_inject = random.randint(100) <= probability
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
                cpp_inject = CppFileInject({
                    "head_file": head_file_path,
                    "source_file": source_file_path,
                    "tpl_folder": self.tpl_folder_path,
                    "generate_field": generate_field_count,
                    "generate_method":generate_method_count,
                    "max_parameter": parameter_count,
                    "call_others": self.inject_config["call_others"]
                })
                cpp_inject.inject_code()
                return True
            else:
                print("===>cpp code inject source file or head file not exists of %s" % file_path_without_ext)
        else:
            print("===>cpp code inject skip %s" % file_path)
        return False

    def _inject_dir(self, folder_path, include_rules=None):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join((folder_path, file_name))
            if os.path.isdir(file_path):
                self._inject_dir(file_path, include_rules)
            elif os.path.isfile(file_path):
                if utils.in_rules(file_path, include_rules):
                    self._inject_file(file_path)

    def inject_files(self,files, inject_config):
        self.inject_config = inject_config
        if "include" in self.inject_config:
            include_rules = self.inject_config["include"]
        else:
            include_rules = "*.h"
        self._injected_files = {}
        include_rules = utils.convert_rules(include_rules)

        for file_path in files:
            if os.path.isdir(file_path, include_rules):
                self._inject_dir(file_path, include_rules)
            elif os.path.isfile(file_path):
                # config file force inject
                self._inject_file(file_path, True)
