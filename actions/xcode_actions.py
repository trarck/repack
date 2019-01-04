import os
from action import Action
from project import IosProject


class XCodeRenameAction(Action):
    def run(self, args):
        xcode_project_path = self.get_full_path_from_config("xcode_project_path", self.runner.project_root_path)

        package_id = self.translate_string(self.config["package_id"])

        if "target_name" in self.config:
            target_name = self.translate_string(self.config["target_name"])
        else:
            target_name = self.name

        if "display_name" in self.config:
            display_name = self.translate_string(self.config["display_name"])
        else:
            display_name = target_name

        xcode_project_name = None
        if "xcode_project_name" in self.config:
            xcode_project_name = self.translate_string(self.config["xcode_project_name"])

        product_name = None
        if "product_name" in self.config:
            product_name = self.translate_string(self.config["product_name"])

        new_scheme = None
        if "new_scheme" in self.config:
            product_name = self.translate_string(self.config["new_scheme"])

        old_scheme = None
        if "old_scheme" in self.config:
            product_name = self.translate_string(self.config["old_scheme"])

        ios_project = IosProject(xcode_project_path)
        ios_project.rename(target_name, package_id, display_name, xcode_project_name, product_name, new_scheme,
                           old_scheme)


class XCodeSetCodeSignAction(Action):
    def run(self, args):
        xcode_project_path = self.get_full_path_from_config("xcode_project_path", self.runner.project_root_path)

        code_sign_identity = self.translate_string(self.config["code_sign_identity"])
        provisioning_profile = self.translate_string(self.config["provisioning_profile"])

        development_team = None
        if "development_team" in self.config:
            development_team = self.translate_string(self.config["development_team"])

        provisioning_profile_uuid = None
        if "provisioning_profile_uuid" in self.config:
            provisioning_profile_uuid = self.translate_string(self.config["provisioning_profile_uuid"])

        code_sign_entitlements = None
        if "code_sign_entitlements" in self.config:
            code_sign_entitlements = self.translate_string(self.config["code_sign_entitlements"])

        ios_project = IosProject(xcode_project_path)
        ios_project.set_code_sign(code_sign_identity, provisioning_profile, development_team, provisioning_profile_uuid,
                                  code_sign_entitlements)


class XCodeAddFilesAction(Action):
    def run(self, args):
        xcode_project_path = self.get_full_path_from_config("xcode_project_path", self.runner.project_root_path)
        config = self.config

        files = config["files"]
        for i in range(len(files)):
            files[i] = self.translate_string(files[i])
            if not os.path.isabs(files[i]):
                files[i] = os.path.join(self.runner.project_root_path, files[i])

        parent = None
        if "parent" in config:
            parent = self.translate_string(config["parent"])

        ios_project = IosProject(xcode_project_path)
        ios_project.add_files(files, parent)


class XCodeBuildAppAction(Action):
    def run(self, args):
        xcode_project_path = self.get_full_path_from_config("xcode_project_path", self.runner.project_root_path)
        config = self.config

        target = self.translate_string(config["target"])
        configuration = self.translate_string(config["configuration"])
        sdk = self.translate_string(config["sdk"])
        out_put = self.translate_string(config["out_put"])

        ios_project = IosProject(xcode_project_path)
        ios_project.build_app(target, configuration, sdk, out_put)


class XCodeBuildArchiveAction(Action):
    def run(self, args):
        xcode_project_path = self.get_full_path_from_config("xcode_project_path", self.runner.project_root_path)
        config = self.config

        scheme = self.translate_string(config["scheme"])
        configuration = self.translate_string(config["configuration"])
        out_put = self.translate_string(config["out_put"])

        ios_project = IosProject(xcode_project_path)
        ios_project.build_archive(scheme, configuration, out_put)
