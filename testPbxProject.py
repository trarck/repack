import os
from file_crypt import FileCrypt

#FileCrypt.encrypt("data/temp/p.png","data/temp/p.bin","newkey","XXTEAXX")
#FileCrypt.decrypt("data/temp/p.bin","data/temp/p1.png","test","xxtea")
fc=FileCrypt("newkey","XXTEAXX")
fc.encrypt_dir("data/temp/res_","data/temp/res",[".*\.png"])
#fc.decrypt_dir("data/temp/projects/game1/res","data/temp/tttt",[".*\.png"])
