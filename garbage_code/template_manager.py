import os
from Cheetah.Template import Template


class TemplateManager:
    template_dir = ""

    @staticmethod
    def set_dir(folder_path):
        TemplateManager.template_dir = folder_path

    @staticmethod
    def get_data(template_file_path, search_list):
        if not os.path.isabs(template_file_path):
            template_file_path = os.path.join(TemplateManager.template_dir, template_file_path)
        tpl = Template(file=template_file_path,
                       searchList=search_list)
        return str(tpl)

    @staticmethod
    def get_cpp_data(template_file_path, search_list):
        return TemplateManager.get_data(os.path.join("cpp", template_file_path), search_list)

    @staticmethod
    def get_objc_data(template_file_path, search_list):
        return TemplateManager.get_data(os.path.join("objc", template_file_path), search_list)

    @staticmethod
    def get_obf_data(template_file_path, search_list):
        return TemplateManager.get_data(os.path.join("obf", template_file_path), search_list)
