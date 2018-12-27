import os
import random
import shutil
import json
import plistlib

from resource.directory_generator import DirectoryGenerator
from generater import RandomGenerater
from path_crypt import PathCrypt


class ResourceMapping:
    def __init__(self,out_res_path,dirs,remove_source, keep_ext=True):
        self.out_res_path = out_res_path
        self.dirs=dirs
        self.remove_source = remove_source
        self.keep_ext = keep_ext

        self.map = None

    def mapping(self,src_res_path, rule,ignore_root=False):
        # generate mapping dir
        self.map = {}
        self.parse_dir(src_res_path,rule)

    def parse_dir(self, src_folder_path, rule, relative_path=""):
        # get all files
        print("===>parse dir %s" % src_folder_path)
        files = os.listdir(src_folder_path)
        for filename in files:
            file_path = os.path.join(src_folder_path, filename)
            rel_path = relative_path + ("/" if relative_path else "") + filename

            if not rule or rule.test(rel_path):
                if os.path.isdir(file_path):
                    self.parse_dir(file_path, rule, rel_path)
                elif os.path.isfile(file_path):
                    self.parse_file(file_path, rel_path)
                else:
                    print("ohters:%s" % filename)

    def parse_file(self, src_file, relative_path):
        out_dir = random.choice(self.dirs)
        out_file_name = RandomGenerater.generate_words(1, 2)
        if self.keep_ext:
            out_file_name += os.path.splitext(src_file)[1]
        out_relative_path = out_dir + "/" + out_file_name
        out_path = os.path.join(self.out_res_path, out_relative_path)
        # copy to out_dir
        if self.remove_source:
            os.rename(src_file,out_path)
        else:
            shutil.copyfile(src_file, out_path)
        self.map[relative_path] = out_relative_path

    def save_mapping_data(self, out_mapping_file, crypt, save_json=True, save_plist=True):
        if not out_mapping_file:
            out_mapping_file = os.path.join(self.out_res_path, RandomGenerater.generate_words(1, 2))

        if crypt:
            map_data = {}
            for k, v in self.map.items():
                k = PathCrypt.path_md5(k, crypt)
                map_data[k] = v
        else:
            map_data = self.map

        if save_json:
            fp = open(out_mapping_file + ".json", "w+")
            json.dump(map_data, fp)
            fp.close()

        if save_plist:
            plist_file_path = out_mapping_file + ".plist"
            print("save to %s"%plist_file_path)
            plistlib.writePlist(map_data, plist_file_path)
