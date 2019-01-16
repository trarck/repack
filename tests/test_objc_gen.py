import unittest

from garbage_code.objc_generator import *
from garbage_code.objc_garbage_code import ObjcFile

class ObjcGenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("in setup class")
        cls.tpl_folder_path= os.path.join(os.path.dirname(__file__), "../data/template/objc")

    @classmethod
    def tearDownClass(cls):
        print("in tear down class")

    def setUp(self):
        print("in setup")

    def tearDown(self):
        print("in tear down")

    def test_gen_function(self):
        method_name = "myfun"
        parameters = []
        parameter_count = 3
        for i in range(parameter_count):
            param_type = CType("int")
            parameter = CParameter("param%d"%i, param_type,"" if i==0 else "withParam%d"%i)
            parameters.append(parameter)

        return_type = CType("float")

        fun = ObjcMethod(method_name, parameters, return_type, self.tpl_folder_path)

        self.assertIsNotNone(fun.get_def_string())
        self.assertIsNotNone(fun.get_call_string())
        self.assertIsNotNone(fun.get_code_string())

        # print(fun.get_def_string())
        # print(fun.get_call_string())
        # print(fun.get_code_string())

    def test_gen_class(self):
        cls= ObjcGenerator.generate_class(self.tpl_folder_path,3,5,3,80)
        # print(cls.get_def_string())
        # print(cls.get_code_string())
        print(cls.get_stack_instance_def("test"))
        self.assertIsNotNone(cls.get_def_string())
        self.assertIsNotNone(cls.get_code_string())

    def test_gen_class_to_file(self):
        head_file_name = "cpp_files/gen/objc/a.h"
        source_file_name = "cpp_files/gen/objc/a.mm"
        generator = ObjcFile({
            "head_file": head_file_name,
            "source_file": source_file_name,
            "tpl_folder": self.tpl_folder_path,
            "class_name": "A",
            "namespace": None,
            "field_count": 3,
            "method_count": 5,
            "parameter_count": 3,
            "return_probability": 80,
            "call_others": True,
            "search_path":"cpp_files/gen/objc"
        })

        generator.prepare()
        generator.generate_code()

        self.assertTrue(os.path.exists(head_file_name))
        self.assertTrue(os.path.exists(source_file_name))

if __name__ == '__main__':
    unittest.main()