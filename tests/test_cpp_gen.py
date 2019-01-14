import unittest

from garbage_code.cpp_generator import *

class CppGenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("in setup class")
        cls.tpl_folder_path= os.path.join(os.path.dirname(__file__), "../data/template/cpp_new")

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
            parameter = CParameter("param%d"%i, param_type)
            parameters.append(parameter)

        return_type = CType("float")

        fun = CppMethod(method_name, parameters, return_type, self.tpl_folder_path)

        self.assertEqual(fun.get_def_string().strip(),"virtual float myfun(int param0,int param1,int param2);")
        self.assertIsNotNone(fun.get_call_string())
        self.assertIsNotNone(fun.get_code_string())

    def test_gen_class(self):
        cls= CppGenerator.generate_class(self.tpl_folder_path,3,5,3,80)
        self.assertIsNotNone(cls.get_def_string())
        self.assertIsNotNone(cls.get_code_string())

if __name__ == '__main__':
    unittest.main()