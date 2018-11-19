import os
import shutil
import plistlib
import subprocess

from pbxproj import XcodeProject, PBXProvioningTypes


class IosProject:
    def __init__(self, project_file_path):

        if project_file_path.find(".xcodeproj") > -1:
            self.project_file_path = project_file_path
            self.project_root = os.path.dirname(project_file_path)
        else:
            self.project_root = project_file_path
            self.project_file_path = self._get_xcode_project_file_path(project_file_path)

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
                    if build_configuration is None or build_configuration.buildSettings is None:
                        continue
                    if "SDKROOT" in build_configuration.buildSettings and build_configuration.buildSettings.SDKROOT == "iphoneos":
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

    def rename_xcode_project(self, new_project_file_name):
        if not self.project_file_path:
            raise "Can't find xocde project in " % self.project_root

        if new_project_file_name.find(".xcodeproj") == -1:
            new_project_file_name += ".xcodeproj"

        if os.path.basename(self.project_file_path) == new_project_file_name:
            # the project_file is same as old
            return self.project_file_path

        # rename project_file to new
        new_project_file_path = os.path.join(self.project_root, new_project_file_name)
        print("===>rename project file %s to %s" % (self.project_file_path, new_project_file_path))
        if os.path.exists(new_project_file_path):
            shutil.rmtree(new_project_file_path)
        os.rename(self.project_file_path, new_project_file_path)
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
            print("===>get info_plist_file_path %s" % os.path.join(self.project_root, info_plist_file_path))
            root_obj = plistlib.readPlist(os.path.join(self.project_root, info_plist_file_path))
            root_obj['CFBundleIdentifier'] = package_id
            root_obj['CFBundleDisplayName'] = display_name
            plistlib.writePlist(root_obj, os.path.join(self.project_root, info_plist_file_path))

    def rename(self, target_name, package_id, display_name, new_project_file_name=None, product_name=None):
        if not new_project_file_name:
            new_project_file_name = target_name
        xcode_project_file_path = self.rename_xcode_project(new_project_file_name)

        # open pbx project
        pbx_proj_file_path = os.path.join(xcode_project_file_path, "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        self.rename_target(pbx_project, target_name, product_name)
        self.set_plist(pbx_project, package_id, display_name)
        ios_app_target = self._get_ios_app_target(pbx_project)
        if ios_app_target:
            for configuration in pbx_project.objects.get_configurations_on_targets(ios_app_target.name):
                print(configuration.buildSettings[u"PRODUCT_BUNDLE_IDENTIFIER"])
                if u"PRODUCT_BUNDLE_IDENTIFIER" in configuration.buildSettings:
                    configuration.set_flags(u"PRODUCT_BUNDLE_IDENTIFIER", package_id)
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
                      provisioning_profile_uuid=None, code_sign_entitlements=None):
        print("===> set code sign identity=%s,profile=%s,team=%s,profile_uuid=%s,entitlements=%s" %
              (code_sign_identity, provisioning_profile, development_team, provisioning_profile_uuid,
               code_sign_entitlements))
        xcode_project_file_path = self._get_xcode_project_file_path(self.project_root)
        pbx_proj_file_path = os.path.join(xcode_project_file_path, "project.pbxproj")
        pbx_project = XcodeProject.load(pbx_proj_file_path)
        ios_app_target = self._get_ios_app_target(pbx_project)
        if ios_app_target:
            target_name = ios_app_target.name
            pbx_project.set_flags(u'CODE_SIGN_IDENTITY', code_sign_identity, target_name)
            pbx_project.set_flags(u'CODE_SIGN_IDENTITY[sdk=iphoneos*]', code_sign_identity, target_name)
            pbx_project.set_flags(u'PROVISIONING_PROFILE_SPECIFIER', provisioning_profile, target_name)
            if development_team:
                pbx_project.set_flags(u'DEVELOPMENT_TEAM', development_team, target_name)

            if provisioning_profile_uuid:
                pbx_project.set_flags(u'PROVISIONING_PROFILE', provisioning_profile_uuid, target_name)

            if code_sign_entitlements:
                pbx_project.set_flags(u'CODE_SIGN_ENTITLEMENTS', code_sign_entitlements, target_name)

            for target in pbx_project.objects.get_targets(target_name):
                pbx_project.objects[pbx_project.rootObject].set_provisioning_style(PBXProvioningTypes.MANUAL, target)

            pbx_project.save()

    def add_file(self, file_path, parent):
        pbx_project = XcodeProject.load(os.path.join(self.project_file_path, "project.pbxproj"))

        if parent is not None:
            parents = pbx_project.get_groups_by_name(parent)
            if parents is not None:
                parent = parents[0]

        pbx_project.add_file(file_path, parent)
        pbx_project.save()

    def build_app(self, target, configuration, sdk, out_put):
        # build_cmd = 'xcodebuild -project %s -target %s -sdk %s -configuration %s' % (
        # self.project_file_path, target, sdk, configuration)
        # print build_cmd
        # process = subprocess.Popen(build_cmd, shell=True)
        #
        # process.wait()

        build_dir = os.path.join(os.path.dirname(self.project_file_path), "./build/%s-iphoneos" % configuration)
        sign_app = os.path.join(build_dir, "%s.app" % target)

        if os.path.exists(os.path.join(build_dir, "Payload")):
            shutil.rmtree(os.path.join(build_dir, "Payload"))
        else:
            os.makedirs(os.path.join(build_dir, "Payload"))

        shutil.copytree(sign_app, os.path.join(build_dir, "Payload", "%s.app" % target))
        zip_cmd = 'zip -r %s %s' % (out_put, os.path.join(build_dir, "Payload"))
        print zip_cmd
        process = subprocess.Popen(zip_cmd, shell=True)

        process.communicate()

    def build_archive(self, scheme, configuration, out_archive, out_app=None):
        out_dir = os.path.dirname(out_archive)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        print "archiveDir: " + out_archive
        archive_cmd = 'xcodebuild archive -project %s -scheme %s -configuration %s -archivePath %s' % (
            self.project_file_path, scheme, configuration, out_archive)
        process = subprocess.Popen(archive_cmd, shell=True)
        process.wait()

        if out_app:
            export_archive_cmd = 'xcodebuild -exportArchive -archivePath %s -exportPath %s -exportFormat IPA' % (
                out_archive, out_app)
            process = subprocess.Popen(export_archive_cmd, shell=True)

        process.communicate()
