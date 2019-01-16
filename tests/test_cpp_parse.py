import unittest
from cparser.parser import Parser
from pprint import pprint
from garbage_code.gc_utils import group_functions

class CppParseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("in setup class")

    @classmethod
    def tearDownClass(cls):
        print("in tear down class")

    def setUp(self):
        print("in setup")

    def tearDown(self):
        print("in tear down")

    # def test_parse_simple(self):
    #     parser = Parser({
    #         "clang_args": [
    #             "-x", "c++",
    #             "-I./cpp_files"
    #         ]
    #     })
    #
    #     parser.parse_file("./cpp_files/namespace.cpp")
    #
    #     groups=group_functions(parser.functions)
    #
    #     for k,v in groups.items():
    #         print k
    #         for f in v["functions"]:
    #             print f.name

    def test_get_ast_simple(self):
        parser = Parser({
            "clang_args": [
                "-x", "c++",
                "-I./cpp_files"
            ]
        })


        ast = parser.get_ast("./cpp_files/namespace.cpp",False,10,False)
        self.assertIsNotNone(ast)

        pprint(('nodes', ast))


if __name__ == '__main__':
    unittest.main()