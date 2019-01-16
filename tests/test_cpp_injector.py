import unittest
import os

from garbage_code.cpp_source_injector import CppSourceInjector
from garbage_code.cpp_injector import CppInjector


class CppInjectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("in setup class")
        cls.cpp_tpl_folder_path = os.path.join(os.path.dirname(__file__), "../data/template/cpp")
        cls.obf_tpl_folder_path = os.path.join(os.path.dirname(__file__), "../data/template/obf")

    @classmethod
    def tearDownClass(cls):
        print("in tear down class")

    def setUp(self):
        print("in setup")

    def tearDown(self):
        print("in tear down")

    def test_source_inject(self):
        cpp_class_options = {
            "min_field_count": 3,
            "max_field_count": 6,
            "min_method_count": 3,
            "max_method_count": 6,
            "min_parameter_count": 3,
            "max_parameter_count": 6,
            "min_return_probability": 60,
            "max_return_probability": 90
        }

        clang_args = ["-x", "c++",
                "-I./cpp_files","-I./cpp_files/injector"]
        cpp_injector = CppSourceInjector(cpp_class_options, None, clang_args, self.cpp_tpl_folder_path,
                                         self.obf_tpl_folder_path)
        cpp_injector.inject("cpp_files/injector/namespace.cpp")

    # def test_inject_dir(self):
    #     config = {
    #         "probability":100,
    #         "obf_tpl_dir": "../data/template/obf",
    #         "cpp_tpl_dir": "../data/template/cpp",
    #         "class": {
    #             "min_field_count": 3,
    #             "max_field_count": 6,
    #             "min_method_count": 3,
    #             "max_method_count": 6,
    #             "min_parameter_count": 3,
    #             "max_parameter_count": 6,
    #             "min_return_probability": 60,
    #             "max_return_probability": 90
    #         },
    #         "clang_args": []
    #     }
    #     files = ["cpp_files/injector"]
    #
    #     cpp_injector = CppInjector(config)
    #     cpp_injector.inject_files(files)


if __name__ == '__main__':
    unittest.main()
