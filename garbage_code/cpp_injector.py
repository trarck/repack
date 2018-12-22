import os
import random

from pbxproj import XcodeProject
from Cheetah.Template import Template
from native import NativeType, NativeField, NativeParameter, NativeFunction, NativeClass
from cparser.parser import Parser
import utils


class CppFileInjector:
    def __init__(self, options):
        self.options = options
        if "clang_args" in options:
            self.clang_args = options["clang"]
        else:
            self.clang_args = []

        self.tpl_folder_path = options["tpl_folder"]

    def inject(self, file_path, opts=None):
        # parse options
        if opts is None:
            opts = {}
        else:
            opts = opts.copy()

        if "clang_args" in opts:
            clang_args = opts["clang_args"][:]
            clang_args.extend(self.clang_args)
            opts["clang_args"] = clang_args
        else:
            opts["clang_args"] = self.clang_args

        # parse file
        parser = Parser(opts)
        parser.parse_file(file_path)

        # get implementation method
        # get from define
        functions = parser.functions
        impl_funcs = []
        for func in functions:
            if func.is_implement:
                impl_funcs.append(func)

        # get from class define
        for cls in parser.parsed_classes:
            for func in cls.methods:
                if func.is_implement:
                    impl_funcs.append(func)

        # start inject function.
        for func in impl_funcs:
            self._inject_function(func)

    def _inject_function(self, function_info):
        if function_info.root_statement:
            inject_positions = function_info.get_top_statement_end_positions()
            if inject_positions:
                inject_pos_index = random.randrange(0, len(inject_positions))
                inject_pos = inject_positions[inject_pos_index]

    def _gen_inject_code(self):
        p = random.randrange(0, 10)
        # now use two code type
        if p > 4:
            num = []
            for _ in range(0, 3):
                num.extend(utils.generate_int())

            code_tpl = Template(file=os.path.join(self.tpl_folder_path, "one_int.cpp"),
                                searchList=[{"num": num}])
            return str(code_tpl)
        else:
            num = []
            for _ in range(0, 6):
                num.extend(utils.generate_float())

            num.sort()
            code_tpl = Template(file=os.path.join(self.tpl_folder_path, "one_float.cpp"),
                                searchList=[{"num": num}])
            return str(code_tpl)


class CppClassInjector:
    def __init__(self):
        print("inject code to cpp class")


class CppFunctionInjector:
    def __init__(self):
        print("inject code to cpp function.contain class method")
