import unittest
from cparser.parser import Parser
from pprint import pprint


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

    def test_parse_simple(self):
        parser = Parser({
            "clang_args": [
                "-x", "c++",
                "-I./cpp_files"
            ]
        })

        ast = parser.get_ast("./cpp_files/a.cpp")
        self.assertIsNotNone(ast)

        # pprint(('nodes', ast))
