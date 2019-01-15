# -*- coding: utf-8 -*-
import os
import random
import warnings

from Cheetah.Template import Template
from cparser.parser import Parser
from rules import *
from generater import RandomGenerater
from cpp_source_injector import CppSourceInjector
import utils


class CppFunctionInjector:
    """
    向函数内插入代码。包括普通函数和类的方法。
    代码是可以单独存在不需要依赖外部变量。
    """

    def __init__(self, options, ruler=None):
        self.options = options
        if "clang_args" in options:
            self.clang_args = options["clang_args"]
        else:
            self.clang_args = []

        self.tpl_folder_path = options["tpl_folder"]
        self.ruler = ruler

    def inject(self, file_path, opts=None):

        print("===> function inject:%s" % file_path)
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

        print("==>have functions %s" % len(parser.functions))
        # get implementation method
        # get from define
        functions = parser.functions
        impl_funcs = []
        for func in functions:
            if func.is_implement:
                if self.ruler:
                    class_name = func.class_name if func.class_name else "*"
                    if self.ruler.should_skip(class_name, func.name):
                        impl_funcs.append(func)
                else:
                    impl_funcs.append(func)

        # get from class define
        for _, cls in parser.parsed_classes.items():
            for func in cls.methods:
                if func.is_implement:
                    if self.ruler:
                        class_name = func.class_name if func.class_name else "*"
                        if self.ruler.should_skip(class_name, func.name):
                            impl_funcs.append(func)
                    else:
                        impl_funcs.append(func)

        print("==>have impl functions %s" % len(impl_funcs))

        fp = open(file_path, "rU")
        lines = fp.readlines()
        fp.close()

        # start inject function.
        for func in impl_funcs:
            self._inject_function(func, lines)

        if "out" in opts:
            out_file_path = opts["out"]
        else:
            out_file_path = file_path

        fp = open(out_file_path, "w+")
        fp.writelines(lines)
        fp.close()

    def _inject_function(self, function_info, lines):
        if function_info.root_statement:
            inject_positions = function_info.get_top_statement_start_positions()
            if inject_positions:
                inject_pos_index = random.randrange(0, len(inject_positions))
                inject_pos = inject_positions[inject_pos_index]
                var_declare, inject_code = self._gen_inject_code()

                # 先插入实现代码
                line_index = inject_pos[0] - 1
                if line_index > -1 or line_index < len(lines):
                    line = lines[line_index]
                    lines[line_index] = line[:inject_pos[1] - 1] + inject_code + line[inject_pos[1] - 1:]

                    # 再插入定义。定义放在最开头。
                    # 这里要在插入代码之后再插入定义，防止原函数只有一行，插入错误。
                    # 因为定义要插入到前面，如果先插入定义，原来分析出来的插入代码的位置就是错误的。
                    # 先插入代码，因为是在后面，所以不影响定义的插入。
                    begin_line = function_info.root_statement.location.line - 1
                    begin_column = function_info.root_statement.location.column
                    line = lines[begin_line]
                    lines[begin_line] = line[:begin_column] + var_declare + line[begin_column:]
                else:
                    print("Error:outline index:%d,%d" % (line_index, len(lines)))

    def _gen_inject_code(self):
        p = random.randrange(0, 10)
        # now use two code type
        if p > 4:
            num = []
            for _ in range(0, 3):
                num.append(RandomGenerater.generate_int())

            tpl_data = {"num": num, "var_name": RandomGenerater.generate_string()}
            code_tpl_declare = Template(file=os.path.join(self.tpl_folder_path, "one_int_declare.cpp"),
                                        searchList=[tpl_data])

            code_tpl = Template(file=os.path.join(self.tpl_folder_path, "one_int.cpp"),
                                searchList=[tpl_data])
            return str(code_tpl_declare), str(code_tpl)
        else:
            num = []
            for _ in range(0, 6):
                num.append(RandomGenerater.generate_float())

            num.sort()
            tpl_data = {"num": num, "var_name": RandomGenerater.generate_string()}
            code_tpl_declare = Template(file=os.path.join(self.tpl_folder_path, "one_float_declare.cpp"),
                                        searchList=[tpl_data])

            code_tpl = Template(file=os.path.join(self.tpl_folder_path, "one_float.cpp"),
                                searchList=[tpl_data])
            return str(code_tpl_declare), str(code_tpl)


class CppClassInjector:
    """
    向类插入属性和方法。并在原方法中调用新生成的属性和方法。
    """

    def __init__(self):
        print("inject code to cpp class")


class CppInjector:
    default_class_options = {
        "min_field_count": 3,
        "max_field_count": 6,
        "min_method_count": 30,
        "max_method_count": 60,
        "min_parameter_count": 3,
        "max_parameter_count": 8,
        "min_return_probability": 60,
        "max_return_probability": 90
    }

    def __init__(self, options):
        self.options = options
        self._injected_files = None
        self.obf_tpl_folder_path = options["obf_tpl_dir"]
        self.cpp_tpl_folder_path = options["cpp_tpl_dir"]
        self.skips = {}
        self.clang_args = options["clang_args"] if "clang_args" in options else []
        self._success_injected_files = []
        if "class" in self.options:
            self.class_options = self.options["class"]
        else:
            self.class_options = CppInjector.default_class_options
        self._init_rule()

    def _init_rule(self):

        # init file rule
        if "include" in self.options:
            include_rules = self.options["include"]
        else:
            include_rules = ["*.cpp"]

        exclude_rules = None
        if "exclude" in self.options:
            exclude_rules = self.options["exclude"]

        self.file_rule = utils.create_rules(include_rules, exclude_rules)

        # init skip rule
        if 'skips' in self.options:
            if isinstance(self.options['skip'], str):
                list_of_skips = re.split(",\n?", self.options['skips'])
                for skip in list_of_skips:
                    class_name, methods = skip.split("@")
                    self.skips[class_name] = []
                    match = re.match("\[([^]]+)\]", methods)
                    if match:
                        self.skips[class_name] = match.group(1).split(" ")
                    else:
                        raise Exception("invalid list of skip methods")
            else:
                self.skips = self.options['skip']

    def should_skip(self, class_name, method_name, verbose=False):
        if class_name == "*" and "*" in self.skips:
            for func in self.skips["*"]:
                if re.match(func, method_name):
                    return True
        else:
            for key in self.skips.iterkeys():
                if key == "*" or re.match("^" + key + "$", class_name):
                    if verbose:
                        print "%s in skips" % (class_name)
                    if len(self.skips[key]) == 1 and self.skips[key][0] == "*":
                        if verbose:
                            print "%s will be skipped completely" % (class_name)
                        return True
                    if method_name != None:
                        for func in self.skips[key]:
                            if re.match(func, method_name):
                                if verbose:
                                    print "%s will skip method %s" % (class_name, method_name)
                                return True
        if verbose:
            print "%s will be accepted (%s, %s)" % (class_name, key, self.skips[key])
        return False

    def _inject_file(self, file_path, force=False):
        if file_path in self._injected_files:
            return False

        print("===>inject file %s " % (file_path))

        self._injected_files[file_path] = True

        if not force:
            probability = self.options["probability"]
            need_inject = random.randint(0, 100) <= probability
        else:
            need_inject = True

        if need_inject:
            cpp_source_injector = CppSourceInjector(self.class_options, self, self.clang_args, self.cpp_tpl_folder_path,
                                                    self.obf_tpl_folder_path)

            cpp_source_injector.inject(file_path)
            try:
                # cpp_source_injector.inject(file_path)
                self._success_injected_files.append(file_path)
            except Exception, e:
                #warnings.warn(e.message)
                raise e

        else:
            print("===>code inject skip %s" % file_path)
        return False

    def _inject_dir(self, folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isdir(file_path):
                self._inject_dir(file_path)
            elif os.path.isfile(file_path):
                print("#Rule:%s=%s" % (file_path, str(self.file_rule.test(file_path))))
                # dir file check is match file rule
                if not self.file_rule or self.file_rule.test(file_path):
                    self._inject_file(file_path)

    def inject_files(self, files):
        self._injected_files = {}

        for file_path in files:
            if os.path.isdir(file_path):
                self._inject_dir(file_path)
            elif os.path.isfile(file_path):
                # config file force inject
                self._inject_file(file_path, True)

        print("inject %d files" % len(self._success_injected_files))
        for f in self._success_injected_files:
            print("==> inject %s" % f)
