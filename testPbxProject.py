import os
import utils

utils.copy_files_with_rules("data/temp/aaa","data/temp/aaa","data/temp/ddd",exclude=utils.convert_rules(["*.txt"]))

