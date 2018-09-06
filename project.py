import os
import shutil
import plistlib

from pbxproj import XcodeProject, PBXProvioningTypes


class IosProject:
    def __init__(self, project_root):
        self.project_root = project_root

    def _get_xcode_project_file_path(self, project_dir):
        files = os.listdir(project_dir)
        for filename in files:
            if filename.find(".xcodeproj") > -1:
                return os.path.join(project_dir, filename)
        return None

    def _get_ios_app_target(self, pbx_project):
        targets = pbx_project.objects.get_targets()

        ios_app_target = None
        for target in targets:
            if target.productType == "com.apple.product-type.application":
                # check build config sdkroot
                configuration_list = pbx_project.objects[target.buildConfigurationList]
                if configuration_list is None:
                    print("can't find configuration list of %s" % target.buildConfigurationList)
                    continue
                for conf_id in configuration_list.buildConfigurations:
                    build_configuration = pbx_project.objects[conf_id]
                    if build_configuration is None:
                        continue
                    if build_configuration.buildSettings.SDKROOT == "iphoneos":
                        return target
        return None

    def _get_ios_info_plist_file_path(self, pbx_project):
        ios_app_target = self._get_ios_app_target(pbx_project)
        if ios_app_target:
            configuration_list = pbx_project.objects[ios_app_target.buildConfigurationList]
            # default two configuration debug and release are same info.plist
            build_configuration = pbx_project.objects[configuration_list.buildConfigurations[0]]
            return build_configuration.buildSettings.INFOPLIST_FILE
        return None

    def rename_xcode_project(self, project_file_name):
        xcode_project_file_path = self._get_xcode_project_file_path(self.project_root)
        if not xcode_project_file_path:
            raise "Can't find xocde project in " % self.project_root

        if project_file_name.find(".xcodeproj") == -1:
            project_file_name += ".xcodeproj"

        if os.path.basename(xcode_project_file_path) == project_file_name:
            # the project_file is same as old
            return xcode_project_file_path

        # rename project_file to new
        new_project_file_path = os.path.join(self.project_root, project_file_name)
        print("===>rename project file %s to %s" % (xcode_project_file_path, new_project_file_path))
        if os.path.exists(new_project_file_path):
            shutil.rmtree(new_project_file_path)
        os.rename(xcode_project_file_path, new_project_file_path)
        return new_project_file_path

    def rename_target(self, pbx_project, target_name, product_name=None, fore=False):
        print("===> rename target target_name=%s,product_name=%s" % (target_name, product_name))
        ios_app_target = self._get_ios_app_target(pbx_project)
        if ios_app_target:

            # change target name
            ios_app_target.name = target_name

            # change productName
            if product_name is None or target_name == product_name:
                ios_app_target.productName = target_name
                product_name = "${TARGET_NAME}"
            else:
                ios_app_target.productName = product_name
                fore = True

            # change build config PRODUCT_NAME
            configuration_list = pbx_project.objects[ios_app_target.buildConfigurationList]
            for conf_id in configuration_list.buildConfigurations:
                build_configuration = pbx_project.objects[conf_id]
                if build_configuration:
                    if "PRODUCT_NAME" in build_configuration.buildSettings or fore:
                        build_configuration.buildSettings.PRODUCT_NAME = product_name

    def set_plist(self, pbx_project, package_id, display_name):
        # get plist file
        print("===>set plist packgage_id=%s,display_name=%s" % (package_id, display_name))
        info_plist_file_path = self._get_ios_info_plist_file_path(pbx_project)
        if info_plist_file_path:
            root_obj = plistlib.readPlist(os.path.join(self.project_root, info_plist_file_path))
            root_obj['CFBundleIdentifier'] = package_id
            root_obj['CFBundleDisplayName'] = display_name
            plistlib.writePlist(root_obj, os.path.join(self.project_root, info_plist_file_path))

    def rename(self, target_name, package_id, display_name, project_file_name=None, product_name=None):
        if not project_file_name:
            project_file_name = target_name
        xcode_project_file_path = self.rename_xcode_project(project_file_name)

        # open pbx project
        pbx_proj_file_path = os.path.join(xcode_project_file_path, "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        self.rename_target(pbx_project, target_name, product_name)
        self.set_plist(pbx_project, package_id, display_name)
        pbx_project.save()

    def set_resource_obfuscate_key(self, crypt_key):
        xcode_project_file_path = self._get_xcode_project_file_path(self.project_root)
        pbx_proj_file_path = os.path.join(xcode_project_file_path, "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        ios_app_target = self._get_ios_app_target(pbx_project)
        if ios_app_target:
            pbx_project.add_other_cflags('-DUSE_RESOURCE_OBFUSCATE -DRESOURCE_OBFUSCATE_KEY=%s' % crypt_key,
                                         ios_app_target.name)

    def set_code_sign(self, code_sign_identity, provisioning_profile, development_team=None,
                      provisioning_profile_uuid=None):
        print("===> set code sign identity=%s,profile=%s,team=%s,profile_uuid=%s" %
              (code_sign_identity, provisioning_profile_uuid, development_team, provisioning_profile_uuid))
        xcode_project_file_path = self._get_xcode_project_file_path(self.project_root)
        pbx_proj_file_path = os.path.join(xcode_project_file_path, "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        ios_app_target = self._get_ios_app_target(pbx_project)
        if ios_app_target:
            target_name = ios_app_target.name
            pbx_project.set_flags(u'CODE_SIGN_IDENTITY[sdk=iphoneos*]', code_sign_identity, target_name)
            pbx_project.set_flags(u'PROVISIONING_PROFILE_SPECIFIER', provisioning_profile, target_name)
            if development_team:
                pbx_project.set_flags(u'DEVELOPMENT_TEAM', development_team, target_name)
            if provisioning_profile_uuid:
                pbx_project.set_flags(u'PROVISIONING_PROFILE', provisioning_profile_uuid, target_name)

            for target in self.objects.get_targets(target_name):
                self.objects[self.rootObject].set_provisioning_style(PBXProvioningTypes.MANUAL, target)
