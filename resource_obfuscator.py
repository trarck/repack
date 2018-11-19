import os
import shutil

import utils
from path_crypt import PathCrypt


class CryptInfo:
    def __init__(self, key, type="md5", out_length=0, random_position=0, with_ext=False):
        self.key = key
        self.type = type
        self.out_length = out_length
        self.random_position = random_position
        self.with_ext = with_ext

    def parse_config(self, crypt_data):
        if "key" in crypt_data:
            self.key = crypt_data["key"]

        if "type" in crypt_data:
            self.type = crypt_data["type"]

        if "out_length" in crypt_data:
            self.out_length = crypt_data["out_length"]

        if "random_position" in crypt_data:
            self.random_position = crypt_data["random_position"]

        if "with_ext" in crypt_data:
            self.with_ext = crypt_data["with_ext"]

    def copy(self):
        return CryptInfo(self.key, self.type, self.out_length, self.random_position, self.with_ext)


class ResourceObfuscator:
    def __init__(self, resource_folder_path, out_folder_path, sub_folders, ignore_folders, crypt_info,
                 include_rules=None, exclude_rules=None,
                 remove_source=False):
        self.resource_folder_path = resource_folder_path
        self.out_folder_path = out_folder_path
        self.sub_folders = []

        if sub_folders:
            for sub_path in sub_folders:
                self.sub_folders.append(os.path.normpath(sub_path))

        self.ignore_folders = []
        if ignore_folders:
            for ignore_path in ignore_folders:
                self.ignore_folders.append(os.path.normpath(ignore_path))

        self.crypt_info = crypt_info
        self.remove_source = remove_source
        if not self.crypt_info.out_length:
            self.crypt_info.out_length = 16
        if not self.crypt_info.random_position:
            self.crypt_info.random_position = 8

        self.include_rules = include_rules
        self.exclude_rules = exclude_rules

    def parse_file(self, src_file, out_folder_path, relative_path):
        print("===>parse file %s relative path %s" % (src_file, relative_path))
        # check rules
        need_crypt = True
        if self.include_rules:
            if not utils.in_rules(src_file, self.include_rules):
                need_crypt = False

        elif self.exclude_rules:
            if utils.in_rules(src_file, self.exclude_rules):
                need_crypt = False

        if need_crypt:
            plain_path = relative_path

            if self.crypt_info.with_ext:
                fes = os.path.splitext(relative_path)
                file_ext = fes[1]

                # use unix path
            plain_path = plain_path.replace("\\", "/")

            if self.crypt_info.type == "md5":
                crypt_path = PathCrypt.md5_path(plain_path, self.crypt_info.key)
            else:
                crypt_path = PathCrypt.xor_path(
                    plain_path,
                    self.crypt_info.key,
                    self.crypt_info.out_length,
                    self.crypt_info.random_position)

            print("===>crypt %s => %s" % (plain_path, crypt_path))

            if self.crypt_info.with_ext:
                crypt_path += file_ext

            out_file = os.path.join(out_folder_path, crypt_path)
        else:
            out_file = os.path.join(out_folder_path, relative_path)

        parent_folder = os.path.dirname(out_file)
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        if self.remove_source:
            os.rename(src_file, out_file)
        else:
            shutil.copyfile(src_file, out_file)

    def parse_dir(self, src_folder_path, out_folder_path, relative_path=""):
        # get all files
        print("===>parse dir %s" % src_folder_path)
        files = os.listdir(src_folder_path)
        for filename in files:
            file_path = os.path.join(src_folder_path, filename)
            rel_path = os.path.join(relative_path, filename)
            if os.path.isdir(file_path):

                if os.path.normpath(rel_path) in self.ignore_folders:
                    # copy to dist
                    utils.copy_files(file_path, os.path.join(out_folder_path, rel_path))
                else:

                    if os.path.normpath(rel_path) in self.sub_folders:
                        self.parse_dir(file_path, os.path.join(out_folder_path, rel_path), "")
                    else:
                        self.parse_dir(file_path, out_folder_path, rel_path)
                        if self.remove_source:
                            os.rmdir(file_path)
            elif os.path.isfile(file_path):
                self.parse_file(file_path, out_folder_path, rel_path)

    def start(self):
        print("===>obfuscate %s,%s" % (self.resource_folder_path, self.out_folder_path))
        if self.resource_folder_path == self.out_folder_path:
            resource_path = self.resource_folder_path
            bak_path = resource_path + "_bak"
            if os.path.exists(bak_path):
                shutil.rmtree(bak_path)
            os.rename(resource_path, bak_path)
            self.resource_folder_path = bak_path
            self.parse_dir(self.resource_folder_path, self.out_folder_path, "")
            if self.remove_source:
                shutil.rmtree(bak_path)
        else:
            self.parse_dir(self.resource_folder_path, self.out_folder_path, "")
