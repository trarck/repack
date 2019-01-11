# -*- coding: utf-8 -*-
import os
import random
from generater import RandomGenerater
from cparser.parser import Parser
from template_manager import TemplateManager
from cpp_generator import CppGenerator

import gc_utils


class InsertInfo:
    def __init__(self, line, column, code):
        """

        :param line: is fixed from zero
        :param column: is fixed from zero
        :param code:
        """
        self.line = line
        self.column = column
        self.code = code


class BaseInsertion:
    def __init__(self):
        self.inserts = []

    def append_inert_info(self, line, column, code):
        self.inserts.append(InsertInfo(line, column, code))


class SegmentCodeInsertion(BaseInsertion):

    def inject(self, functions):
        for func in functions:
            self._inject_function(func)

    def _inject_function(self, function_info):
        if function_info.root_statement:
            inject_positions = function_info.get_top_statement_start_positions()
            if inject_positions:
                inject_pos_index = random.randrange(0, len(inject_positions))
                inject_pos = inject_positions[inject_pos_index]
                var_declare, inject_code = self._gen_inject_code()
                # 代码段插入信息
                self.append_inert_info(inject_pos[0] - 1, inject_pos[1] - 1, inject_code)
                # 定义变量插入信息
                begin_line = function_info.root_statement.location.line - 1
                begin_column = function_info.root_statement.location.column
                self.append_inert_info(begin_line, begin_column, var_declare)

    def _gen_inject_code(self):
        p = random.randrange(0, 10)
        # now use two code type
        if p > 4:
            num = []
            for _ in range(0, 3):
                num.append(RandomGenerater.generate_int())

            tpl_data = {"num": num, "var_name": RandomGenerater.generate_string()}
            code_declare = TemplateManager.get_obf_data("one_int_declare.cpp", [tpl_data])

            code = TemplateManager.get_obf_data("one_int.cpp", [tpl_data])

            return code_declare, code
        else:
            num = []
            for _ in range(0, 6):
                num.append(RandomGenerater.generate_float())

            num.sort()
            tpl_data = {"num": num, "var_name": RandomGenerater.generate_string()}
            code_declare = TemplateManager.get_obf_data("one_float_declare.cpp", [tpl_data])

            code = TemplateManager.get_obf_data("one_float.cpp", [tpl_data])

            return code_declare, code


class ClassCallInsertion(BaseInsertion):

    def spread(self, functions, cpp_class):
        """
        把类的代码分散到源函数之间
        :param functions:
        :param cpp_class:
        """
        for method in cpp_class.methods:
            function_info = random.choice(functions)
            start = function_info.get_extent_start()

            self.append_inert_info(start.line, start.column, method.to_code())

    def inject(self, functions, cpp_class):
        """
        把调用类的方法和属性的代码插入源函数的代码之间
        :param functions:
        :param cpp_class:
        :return:
        """
        for function_info in functions:
            if function_info.root_statement:
                inject_positions = function_info.get_top_statement_start_positions()
                if inject_positions:
                    inject_pos=random.choice(inject_positions)
                    method = random.choice(cpp_class.methods)
                    self.append_inert_info(inject_pos[0] - 1, inject_pos[1] - 1, inject_code)


class CppSourceInjector:
    def __init__(self, cpp_class, source_file, ruler):
        self.cpp_class = cpp_class
        self.source_file = source_file
        self.ruler = ruler

    def do_inserts(self, inserts):
        def insert_cmp(a, b):
            if a.line == b.line:
                return b.colmun - a.colmun
            else:
                return b.line - a.line

        inserts.sort(insert_cmp)

        fp = open(self.source_file, "rU")
        lines = fp.readlines()
        fp.close()

        for insert_info in inserts:
            line = lines[insert_info.line]
            lines[insert_info.line] = line[:insert_info.column] + insert_info.code + line[insert_info.column:]

    def inject(self):
        if not os.path.exists(self.source_file):
            print("===>inject file not exists[%s]" % self.source_file)

        opts = {
            "clang_args": self.clang_args
        }
        cpp_parser = Parser(opts)
        cpp_parser.parse_file(self.source_file)

        sci = SegmentCodeInsertion()
        sci.inject(gc_utils.get_all_implement_functions(cpp_parser, self.ruler))

        cci = ClassCallInsertion()
        cci.spread(gc_utils.get_all_implement_functions(cpp_parser, self.ruler), self.cpp_class)
        cci.inject(gc_utils.get_implement_functions(cpp_parser, self.ruler), self.cpp_class)
        inserts = sci.inserts + cci.inserts

        self.do_inserts(inserts)
