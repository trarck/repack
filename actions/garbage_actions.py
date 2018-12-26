import os
from action import Action
from garbage_code.cpp_garbage_code import CppGarbageCode
from garbage_code.objc_garbage_code import ObjCGarbageCode
from garbage_code.cpp_injector import CppInjector
from resource.resource_garbage import ResourceGarbage


class GenerateCppCodeAction(Action):
    def run(self, args):
        config = self.config

        out_folder_path = self.translate_string(config["out_dir"])
        if not os.path.isabs(out_folder_path):
            out_folder_path = os.path.join(self.runner.project_root_path, out_folder_path)

        tpl_folder_path = self.translate_string(config["tpl_dir"])
        if not os.path.isabs(tpl_folder_path):
            tpl_folder_path = os.path.join(self.runner.global_data_dir, tpl_folder_path)
        tpl_folder_path = tpl_folder_path.encode("utf-8")

        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.runner.project_root_path, xcode_project_path)

        exec_code_file_path = self.translate_string(config["exec_code_file_path"])
        if not os.path.isabs(exec_code_file_path):
            exec_code_file_path = os.path.join(self.runner.project_root_path, exec_code_file_path)

        cpp_code = CppGarbageCode(tpl_folder_path)
        action = cpp_code.generate_cpp_file(out_folder_path, xcode_project_path, exec_code_file_path, config)
        self.runner.do_action(action)


class GenerateObjcCodeAction(Action):
    def run(self, args):
        config = self.config

        out_folder_path = self.translate_string(config["out_dir"])
        if not os.path.isabs(out_folder_path):
            out_folder_path = os.path.join(self.runner.project_root_path, out_folder_path)

        tpl_folder_path = self.translate_string(config["tpl_dir"])
        if not os.path.isabs(tpl_folder_path):
            tpl_folder_path = os.path.join(self.runner.global_data_dir, tpl_folder_path)
        tpl_folder_path = tpl_folder_path.encode("utf-8")

        xcode_project_path = self.translate_string(config["xcode_project_path"])
        if not os.path.isabs(xcode_project_path):
            xcode_project_path = os.path.join(self.runner.project_root_path, xcode_project_path)

        exec_code_file_path = self.translate_string(config["exec_code_file_path"])
        if not os.path.isabs(exec_code_file_path):
            exec_code_file_path = os.path.join(self.runner.project_root_path, exec_code_file_path)

        objc_code = ObjCGarbageCode(tpl_folder_path)
        action = objc_code.generate_cpp_file(out_folder_path, xcode_project_path, exec_code_file_path, config)
        self.runner.do_action(action)


class InjectCppCodeAction(Action):
    def run(self, args):
        config = self.config

        files = config["files"]
        del config["files"]
        checked_files = []
        for file_path in files:
            file_path = self.translate_string(file_path)
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.runner.project_root_path, file_path)
            checked_files.append(file_path)

        tpl_folder_path = self.translate_string(config["tpl_dir"])
        if not os.path.isabs(tpl_folder_path):
            tpl_folder_path = os.path.join(self.runner.global_data_dir, tpl_folder_path)

        tpl_folder_path = tpl_folder_path.encode("utf-8")

        config["tpl_folder"] = tpl_folder_path

        cpp_injector = CppInjector(config)
        cpp_injector.inject_files(checked_files)


class GenerateFilesAction(Action):
    def run(self, args):
        config = self.config

        out_folder_path = self.translate_string(config["out_dir"])
        if not os.path.isabs(out_folder_path):
            out_folder_path = os.path.join(self.project_root_path, out_folder_path)

        rg = ResourceGarbage(out_folder_path, config)
        rg.generate_files()