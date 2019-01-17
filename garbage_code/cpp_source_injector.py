# -*- coding: utf-8 -*-
import os
import random
import shutil
from generater import RandomGenerater
from cparser.parser import Parser
from template_manager import TemplateManager
from cpp_generator import CppGenerator
import gc_utils
import utils


class InsertInfo:
    @staticmethod
    def sort_cmp(a, b):
        if a.line == b.line:
            if b.column == a.column:
                return b.priority - a.priority
            else:
                return b.column - a.column
        else:
            return b.line - a.line

    def __init__(self, line, column, code, priority=0):
        """
        :param line: is fixed from zero
        :param column: is fixed from zero
        :param code:
        :param priority:如果line和column都相同，按priority排序。priority越小排在前面。.
        """
        self.line = line
        self.column = column
        self.code = code
        self.priority = priority


class BaseInsertion:
    def __init__(self, tpl_folder_path):
        self.tpl_folder_path = tpl_folder_path
        self.inserts = []

    def append_inert_info(self, line, column, code, priority=0):
        self.inserts.append(InsertInfo(line, column, code, priority))

    def _inject_function(self, function_info, var_declare, inject_code):
        """
        向函数中插入代码。
        把变量的定义放在最开始，防止C函数，变量定义放在中间出错。
        :param function_info:
        :param var_declare:
        :param inject_code:
        :return:
        """
        if function_info.root_statement:
            inject_positions = function_info.get_top_statement_start_positions()
            if inject_positions:
                inject_pos_index = random.randrange(0, len(inject_positions))
                inject_pos = inject_positions[inject_pos_index]
                # 代码段插入信息
                self.append_inert_info(inject_pos[0] - 1, inject_pos[1] - 1, inject_code)
                # 定义变量插入信息
                begin_line = function_info.root_statement.location.line - 1
                begin_column = function_info.root_statement.location.column
                self.append_inert_info(begin_line, begin_column, var_declare)


class SegmentCodeInsertion(BaseInsertion):
    """
    向函数插入代码段。
    """

    def inject(self, functions):
        for func in functions:
            var_declare, inject_code = self._gen_inject_code()
            self._inject_function(func, var_declare, inject_code)

    def _gen_inject_code(self):
        """
        获取注入代码。
        目前实现二种代码，后面可以加入多种。
        :return:
        """
        p = random.randrange(0, 10)
        # now use two code type
        if p > 4:
            num = []
            for _ in range(0, 3):
                num.append(RandomGenerater.generate_int())

            tpl_data = {"num": num, "var_name": RandomGenerater.generate_string()}
            code_declare = TemplateManager.get_data(os.path.join(self.tpl_folder_path, "one_int_declare.cpp"),
                                                    [tpl_data])

            code = TemplateManager.get_data(os.path.join(self.tpl_folder_path, "one_int.cpp"), [tpl_data])

            return code_declare, code
        else:
            num = []
            for _ in range(0, 6):
                num.append(RandomGenerater.generate_float())

            num.sort()
            tpl_data = {"num": num, "var_name": RandomGenerater.generate_string()}
            code_declare = TemplateManager.get_data(os.path.join(self.tpl_folder_path, "one_float_declare.cpp"),
                                                    [tpl_data])

            code = TemplateManager.get_data(os.path.join(self.tpl_folder_path, "one_float.cpp"), [tpl_data])

            return code_declare, code


class ClassCallInsertion(BaseInsertion):
    """
    在函数之间插入类的方法。并把调用代码插入源函数中。
    """

    def spread(self, functions, cpp_class, lexical_parent):
        """
        把类的代码分散到源函数之间
        :param functions:
        :param cpp_class:
        """
        if functions:
            for method in cpp_class.methods:
                function_info = random.choice(functions)
                start = function_info.get_extent_start()
                self.append_inert_info(start.line - 1, start.column - 1, method.get_code_string())

            # 把类的声明插入块的最上面
            begin_line, begin_column = gc_utils.get_cursor_children_start(lexical_parent)
            self.append_inert_info(begin_line - 1, begin_column - 1, cpp_class.get_def_string())
            # 把引用头插入文件开始处
            self.append_inert_info(0, 0, cpp_class.get_need_includes(), -1000)

    def inject(self, functions, cpp_class):
        """
        把调用类的方法和属性的代码插入源函数的代码之间
        :param functions:
        :param cpp_class:
        :return:
        """
        inst_name = RandomGenerater.generate_string()
        var_declare = cpp_class.get_stack_instance_def(inst_name)
        for function_info in functions:
            if function_info.root_statement:
                method = random.choice(cpp_class.methods)
                self._inject_function(function_info, var_declare, method.get_call_string(inst_name))


class CppSourceInjector:
    Inject_Success = 0
    Inject_Parse_Error = -1,
    Inject_Fail = -2

    def __init__(self, cpp_class_options, ruler, clang_args, cpp_tpl_folder_path, obf_tpl_folder_path):
        """
        对c++源文件进行注入。
        :param cpp_class_options:生成的c++类的配置
        :param ruler:哪些函数是否不用注入。
        :param clang_args:提供给clang的参数
        :param cpp_tpl_folder_path:生成c++代码用的模板。
        :param obf_tpl_folder_path:生成混淆代码模板。
        """
        self.cpp_class_options = cpp_class_options
        self.ruler = ruler
        self.clang_args = clang_args
        self.cpp_tpl_folder_path = cpp_tpl_folder_path
        self.obf_tpl_folder_path = obf_tpl_folder_path

        self.source_file = None

    def _do_inserts(self, source_file, inserts, out_file=None):
        """
        把插入信息写到文件里。
        :param source_file:
        :param inserts:
        :param out_file:
        :return:
        """
        inserts.sort(InsertInfo.sort_cmp)

        fp = open(source_file, "rU")
        lines = fp.readlines()
        fp.close()

        for insert_info in inserts:
            line = lines[insert_info.line]
            lines[insert_info.line] = line[:insert_info.column] + insert_info.code + line[insert_info.column:]

        if not out_file:
            out_file = source_file

        fp = open(out_file, "w+")
        fp.writelines(lines)
        fp.close()

    def gen_cpp_class(self, method_count=0):
        if "method_count_use_define" in self.cpp_class_options and self.cpp_class_options["method_count_use_define"]:
            method_count = gc_utils.get_range_count("method_count", self.cpp_class_options, 5)
        else:
            if not method_count:
                method_count = gc_utils.get_range_count("method_count", self.cpp_class_options, 5)

        field_count = gc_utils.get_range_count("field_count", self.cpp_class_options, 3)
        parameter_count = gc_utils.get_range_count("parameter_count", self.cpp_class_options, 3)
        return_probability = gc_utils.get_range_count("return_probability", self.cpp_class_options, 5)
        return CppGenerator.generate_class(self.cpp_tpl_folder_path, field_count, method_count, parameter_count,
                                           return_probability)

    def inject(self, source_file, out_file=None):
        if not os.path.exists(source_file):
            print("===>inject file not exists[%s]" % source_file)

        opts = {
            "clang_args": self.clang_args
        }

        self.source_file = source_file

        if not out_file:
            out_file = source_file

        cpp_parser = Parser(opts)
        cpp_parser.parse_file(source_file, not utils.is_debug)

        # backup source file
        backup_file_path = source_file + ".bak"
        shutil.copyfile(source_file, backup_file_path)

        if cpp_parser.is_success:
            if not cpp_parser.functions:
                # nothing to injector
                print("===>nothing to injector")
                os.remove(backup_file_path)
                return CppSourceInjector.Inject_Success

            print("===>inject segment code")
            sci = SegmentCodeInsertion(self.obf_tpl_folder_path)
            sci.inject(gc_utils.get_all_implement_functions(cpp_parser, self.ruler))

            inserts = sci.inserts
            print("===>inject class call")
            # get impl functions
            impl_functions = gc_utils.get_implement_functions(cpp_parser, self.ruler)
            # group by namespace
            groups = gc_utils.group_functions(impl_functions)
            for key, group in groups.items():
                cpp_class = self.gen_cpp_class(len(group["functions"]))
                cci = ClassCallInsertion(self.cpp_tpl_folder_path)
                cci.spread(group["functions"], cpp_class, group["cursor"])
                cci.inject(group["functions"], cpp_class)

                inserts = inserts + cci.inserts

            self._do_inserts(source_file, inserts, out_file)

            # check injected file
            if not cpp_parser.check(out_file):
                # have error.restore to source tile
                print("===>restore to origin")
                if utils.is_debug:
                    shutil.move(out_file, out_file+".inj")
                shutil.move(backup_file_path, out_file)
                return self.Inject_Fail
            else:
                os.remove(backup_file_path)
                return self.Inject_Success
        else:
            print("===>inject fall")
            os.remove(backup_file_path)
            return self.Inject_Parse_Error
