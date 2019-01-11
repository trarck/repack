from cpp_base import *


class CppGenerator:
    def __init__(self, tpl_folder_path):
        self.tpl_folder_path = tpl_folder_path

    @staticmethod
    def generate_field():
        field_name = RandomGenerater.generate_string()
        field_type = CType(RandomGenerater.generate_cpp_type())
        return CField(field_name, field_type)

    @staticmethod
    def generate_parameter():
        param_name = RandomGenerater.generate_string()
        param_type = CType(RandomGenerater.generate_cpp_type())
        return CParameter(param_name, param_type)

    @staticmethod
    def generate_function(tpl_folder_path, max_parameter_count=0, return_probability=30):
        method_name = RandomGenerater.generate_string()
        parameters = []
        if max_parameter_count > 0:
            parameter_count = random.randint(0, max_parameter_count)
            for i in range(parameter_count):
                parameter = CppGenerator.generate_parameter()
                parameters.append(parameter)

        # 30% create return type
        if random.randint(0, 100) <= return_probability:
            return_type = CType(CppGenerator.generate_type())
        else:
            return_type = CType(None)

        def_template_file = os.path.join(tpl_folder_path, "function_def.tpl")
        code_template_file = os.path.join(tpl_folder_path, "function_code.tpl")
        call_template_file = os.path.join(tpl_folder_path, "function_call.tpl")
        return CppMethod(method_name, parameters, return_type, def_template_file, code_template_file,
                         call_template_file)

    @staticmethod
    def generate_class(tpl_folder_path, field_count, method_count, max_parameter, method_return_probability,
                       namespace=None):
        # gen fields
        fields = None
        if field_count > 0:
            fields = []
            for i in range(field_count):
                fields.append(CppClass.generate_field())

        # gen mthods
        methods = None
        if method_count > 0:
            methods = []

            for i in range(method_count):
                methods.append(
                    CppGenerator.generate_function(tpl_folder_path, max_parameter, method_return_probability))

        class_name = RandomGenerater.generate_string()
        return CppClass(class_name, fields, methods, "class.h", namespace)
