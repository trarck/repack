import os
import random
import shutil

from directory_generator import DirectoryGenerator
from generater import RandomGenerater


class ResourceMapping:
    def __init__(self, src_res_path, out_res_path, keep_ext=True):
        self.src_res_path = src_res_path
        self.out_res_path = out_res_path
        self.map = None
        self.keep_ext = keep_ext

    def mapping(self, max_level, min_dir_count, max_dir_count):
        # generate mapping dir
        dir_gen = DirectoryGenerator(max_level, min_dir_count, max_dir_count)
        dirs = dir_gen.generate(self.out_res_path)
        self.map = {}
        self.parse_dir(self.src_res_path, dirs)

    def parse_dir(self, src_folder_path, dirs, relative_path=""):
        # get all files
        print("===>parse dir %s" % src_folder_path)
        files = os.listdir(src_folder_path)
        for filename in files:
            file_path = os.path.join(src_folder_path, filename)
            rel_path = os.path.join(relative_path, filename)
            if os.path.isdir(file_path):
                self.parse_dir(file_path, dirs, rel_path)
            elif os.path.isfile(file_path):
                self.parse_file(file_path, dirs, rel_path)
            else:
                print("ohters:%s" % filename)

    def parse_file(self, src_file, dirs, relative_path):
        out_dir = random.choice(dirs)
        out_file_name = RandomGenerater.generate_words(1, 2)
        if self.keep_ext:
            out_file_name += os.path.splitext(src_file)[1]
        out_relative_path = out_dir + "/" + out_file_name
        out_path = os.path.join(self.out_res_path, out_relative_path)
        # copy to out_dir
        shutil.copyfile(src_file, out_path)
        self.map[relative_path] = out_relative_path
