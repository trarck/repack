import os
import utils
import random

from source_file import SourceFile
from Cheetah.Template import Template

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
            for i in range(self.config["generate_method"]):
                methods.append(self.generate_function())

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
        class_define_line, insert_line = self.get_head_class_define_position(lines)
        class_name = self.get_class_name(lines[class_define_line])

        lines.insert(insert_line - 1, head_str)

        fp = open(self.head_file_path, "w+")
        fp.writelines(lines)
        fp.close()

        # insert source
        fp = open(self.source_file_path, "r+")
        lines = fp.readlines()
        fp.close()
        insert_line = self.get_source_last_impl_position(lines)
        lines.insert(insert_line-1, source_str)
        fp = open(self.source_file_path, "w+")
        fp.writelines(lines)
        fp.close()


class CppGarbage:
    def __init__(self):
        print("in cpp garbase")
