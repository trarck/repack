import os
import shutil
import utils
from resource_obfuscator import ResourceObfuscator,CryptInfo

res_path ="data/temp/res"
out_path ="data/temp/res"
sub_dirs = []
crypt_info=CryptInfo("abcd")
res_obf = ResourceObfuscator(res_path, out_path, sub_dirs, crypt_info, False)
res_obf.start()