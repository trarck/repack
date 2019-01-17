# -*- coding: utf-8 -*-
import os
import random
from rules import *
from cpp_source_injector import CppSourceInjector
import utils


class CppInjector:
    """
    像c++源文件中插入代码片段。
    二种插入级别：
        1.在函数之间插入新的函数或类的方法。
        2.在函数内部插入代码片段。
    """
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
        self._parse_error_files = []
        self._inject_fail_files = []

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
        """
        检查哪些方法不用注入
        :param class_name:
        :param method_name:
        :param verbose:
        :return:
        """
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
        """
        按文件注入
        :param file_path:
        :param force:
        :return:
        """
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

            try:
                ret = cpp_source_injector.inject(file_path)
                if ret == CppSourceInjector.Inject_Success:
                    self._success_injected_files.append(file_path)
                elif ret == CppSourceInjector.Inject_Parse_Error:
                    self._parse_error_files.append(file_path)
                elif ret == CppSourceInjector.Inject_Fail:
                    self._inject_fail_files.append(file_path)
            except Exception, e:
                # warnings.warn(e.message)
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

        print("inject success %d,parse error %d,fail %d" % (
        len(self._success_injected_files), len(self._parse_error_files), len(self._inject_fail_files)))
        for f in self._success_injected_files:
            print("==> inject: %s" % f)

        for f in self._parse_error_files:
            print("==> parser error: %s" % f)

        for f in self._inject_fail_files:
            print("==> inject fail: %s" % f)
