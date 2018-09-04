import os
import shutil 

from path_crypt import PathCrypt

class CryptInfo:
    def __init__(self, key,type,out_length,random_position,with_ext=False):
        self.key = key
        self.type=type
        self.out_length = out_length
        self.random_position=random_position
        self.with_ext=with_ext


class ResourceObfuscator:
    def __init__(self, resource_folder_path,out_folder_path,crypt_info,remove_source=False):
        self.resource_folder_path = resource_folder_path
        self.out_folder_path=out_folder_path
        self.crypt_info = crypt_info
        self.remove_source=remove_source
        if not self.crypt_info.out_length:
            self.crypt_info.out_length=16
        if not self.crypt_info.random_position:
            self.crypt_info.random_position=8

    def parse_file(self,src_file,relative_path):
        print("===>parse file %s" % src_file)
        rel_path=os.path.relpath(src_file,self.resource_folder_path)
        print("relative path %s = %s"%(rel_path,relative_path))
        
        plain_path=rel_path
        
        print("****************%s"%self.crypt_info.with_ext)
        if self.crypt_info.with_ext:
            fes=os.path.splitext(rel_path)
            plain_path=fes[0]
            file_ext=fes[1]        
        
        #use unix path
        plain_path=plain_path.replace("\\","/")
        
        if self.crypt_info.type=="md5":
            crypt_path=PathCrypt.md5_path(plain_path,self.crypt_info.key)
        else:
            crypt_path=PathCrypt.xor_path(
                        plain_path,
                        self.crypt_info.key,
                        self.crypt_info.out_length,
                        self.crypt_info.random_position)
        
        print("crypt %s => %s"%(plain_path,crypt_path))
        
        if self.crypt_info.with_ext:
            crypt_path+=file_ext
        
        out_file=os.path.join(self.out_folder_path,crypt_path)
            
        out_folder=os.path.dirname(out_file)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        
        if self.remove_source:
            os.rename(src_file,out_file)
        else:
            shutil.copyfile(src_file,out_file)
            
    def parse_dir(self,src_folder,relative_path=""):
        #get all files
        print("===>parse dir %s" % src_folder)
        files=os.listdir(src_folder)
        for filename in files:
            file_path = os.path.join(src_folder, filename)
            rel_path=os.path.join(relative_path,filename)
            if os.path.isdir(file_path):
                self.parse_dir(file_path,rel_path)
                if self.remove_source:
                    os.rmdir(file_path)
            elif os.path.isfile(file_path):
                self.parse_file(file_path,rel_path)
                
    def start(self):
        if self.resource_folder_path==self.out_folder_path:
            resource_path=self.resource_folder_path
            bak_path=resource_path+"_bak"
            if os.path.exists(bak_path):
                shutil.rmtree(bak_path)
            os.rename(resource_path,bak_path)
            self.resource_folder_path=bak_path
            self.parse_dir(self.resource_folder_path,"")
            if self.remove_source:
                shutil.rmtree(bak_path)
        else:
            self.parse_dir(self.resource_folder_path,"")
        
    