import random
import os
from generater import RandomGenerater

file_exts=["jpg","bin","dat","lua","u3d","ab","mp3","png"]
file_exts_length=len(file_exts)

class ResourceGarbage:
    def __init__(self, out_folder_path,config):
        self.out_folder_path = out_folder_path
        if config is None:
            self.config = {}
        else:
            self.config=config

        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

    @staticmethod
    def generate_ext_name(use_rule_ext_probability=70):
        if random.randint(1,100)<use_rule_ext_probability:
            return file_exts[random.randint(0,file_exts_length-1)]
        else:
            return RandomGenerater.generate_string(2,3).lower()

    @staticmethod
    def generate_content(size):
        buffer = []
        for _ in range(size):
            buffer.append(chr(random.randint(0, 255)))
        return "".join(buffer)

    def generate_file(self,min_size,max_size):
        file_size=random.randint(min_size,max_size)
        file_name=RandomGenerater.generate_words_first_lower(2,3,"_")
        file_ext="."+ResourceGarbage.generate_ext_name()

        fp = open(os.path.join(self.out_folder_path,file_name+file_ext), "w+")
        fp.write(ResourceGarbage.generate_content(file_size))
        fp.close()

    def generate_files(self):
        min_file_count = 16
        if "min_file_count" in self.config:
            min_file_count = self.config["min_file_count"]

        max_file_count = 64
        if "max_file_count" in self.config:
            max_file_count = self.config["max_file_count"]
        file_count=random.randint(min_file_count,max_file_count)

        min_file_size = 128
        if "min_file_size" in self.config:
            min_file_size=self.config["min_file_size"]

        max_file_size=1024*1204
        if "max_file_size" in self.config:
            max_file_size=self.config["max_file_size"]

        for _ in range(file_count):
            self.generate_file(min_file_size,max_file_size)
