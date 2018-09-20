from Cheetah.Template import Template


class NativeType:
    def __init__(self, name=None):
        self.name = name

    def to_string(self, generator):
        if self.name:
            return self.name
        else:
            return "void"


class NativeField:
    def __init__(self, name, field_type, head_tpl_file, source_tpl_file, ):
        self.name = name
        self.native_type = field_type
        self.head_tpl_file = head_tpl_file
        self.source_tpl_file = source_tpl_file

    def generate_code(self, current_class, generator):
        field_h = Template(file=self.head_tpl_file, searchList=[current_class, self])

        field_c = Template(file=self.source_tpl_file, searchList=[current_class, self])

        generator.head_fp.write(str(field_h))
        generator.source_fp.write(str(field_c))

    def to_string(self, current_class, generator):
        field_h = Template(file=self.head_tpl_file, searchList=[current_class, self])

        field_c = Template(file=self.source_tpl_file, searchList=[current_class, self])

        return str(field_h), str(field_c)


class NativeParameter:
    def __init__(self, name, param_type):
        self.name = name
        self.native_type = param_type

    def to_string(self, generator):
        return self.native_type.to_string(generator) + " " + self.name


class NativeFunction:
    def __init__(self, name, parameters, return_type, head_tpl_file, source_tpl_file, base_code=None):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.call_others = []
        self.base_code = base_code
        self.head_tpl_file = head_tpl_file
        self.source_tpl_file = source_tpl_file

    def generate_code(self, current_class, generator):
        function_h = Template(file=self.head_tpl_file, searchList=[current_class, self])

        function_c = Template(file=self.source_tpl_file, searchList=[current_class, self])

        generator.head_fp.write(str(function_h))
        generator.source_fp.write(str(function_c))

    def to_string(self, current_class, generator):
        function_h = Template(file=self.head_tpl_file, searchList=[current_class, self])

        function_c = Template(file=self.source_tpl_file, searchList=[current_class, self])

        return str(function_h), str(function_c)

    def call_other(self, func):
        self.call_others.append(func)


class NativeClass:
    def __init__(self, name, namespace, generator, fields, methods,
                 head_head_tpl_file, head_foot_tpl_file, source_head_tpl_file, source_foot_tpl_file):
        self.class_name = name
        self.namespace = namespace
        self.generator = generator
        self.fields = fields if fields else []
        self.methods = methods if methods else []
        self.head_head_tpl_file = head_head_tpl_file
        self.head_foot_tpl_file = head_foot_tpl_file
        self.source_head_tpl_file = source_head_tpl_file
        self.source_foot_tpl_file = source_foot_tpl_file
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

    def get_full_class_name(self):
        if self.namespace:
            if isinstance(self.namespace, (str)):
                return self.namespace.replace(".", "::") + "::" + self.class_name
            else:
                return "::".join(self.namespace) + "::" + self.class_name
        return self.class_name

    def generate_code(self, generator):
        self.prepare_namespace()
        # gen head
        class_h = Template(file=self.head_head_tpl_file,
                           searchList=[self])

        class_c = Template(file=self.source_head_tpl_file,
                           searchList=[self])

        generator.head_fp.write(str(class_h))
        generator.source_fp.write(str(class_c))

        # gen fileds
        for filed in self.fields:
            filed.generate_code(self, generator)

        for method in self.methods:
            method.generate_code(self, generator)

        # gen foot
        class_h = Template(file=self.head_foot_tpl_file,
                           searchList=[self])

        class_c = Template(file=self.source_foot_tpl_file,
                           searchList=[self])

        generator.head_fp.write(str(class_h))
        generator.source_fp.write(str(class_c))

    def to_string(self, generator):
        self.prepare_namespace()
        head_str = ""
        source_str = ""
        # gen head
        class_h = Template(file=self.head_head_tpl_file,
                           searchList=[self])

        class_c = Template(file=self.source_head_tpl_file,
                           searchList=[self])

        head_str += str(class_h)
        source_str += str(class_c)

        # gen fileds
        for filed in self.fields:
            filed_head_str, filed_source_str = filed.to_string(self, generator)
            head_str += filed_head_str
            source_str += filed_source_str

        for method in self.methods:
            method_head_str, method_source_str = method.to_string(self, generator)
            head_str += method_head_str
            head_str += method_source_str

            # gen foot
        class_h = Template(file=self.head_foot_tpl_file,
                           searchList=[self])

        class_c = Template(file=self.source_foot_tpl_file,
                           searchList=[self])

        head_str += str(class_h)
        source_str += str(class_c)
        return head_str, source_str

    def get_generated_field_method(self, generator):
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

    def get_function_call_code(self, method, generator, index=1):
        call_tpl = Template(file=os.path.join(generator.tpl_folder_path, "call_class_function.cpp"),
                            searchList=[{"method": method, "index": index}, self])
        return str(call_tpl)
