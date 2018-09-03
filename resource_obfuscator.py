import os
import shutil 

from path_crypt import PathCrypt

class ResourceObfuscator:
    def __init__(self, resource_folder_path,out_folder_path,crypt_key,crypt_type,remove_source=False):
        self.resource_folder_path = resource_folder_path
        self.out_folder_path=out_folder_path
        self.crypt_key = crypt_key
        self.crypt_type=crypt_type
        self.remove_source=remove_source

    def parse_file(self,src_file,relative_path):
        print("===>parse file %s" % src_file)
        rel_path=os.path.relpath(src_file,self.resource_folder_path)
        print("relative path %s = %s"%(rel_path,relative_path))
        fes=os.path.splitext(rel_path)
        file_path_without_ext=fes[0]
        file_ext=fes[1]
        if self.crypt_type=="md5":
            crypt_path=PathCrypt.md5_path(file_path_without_ext,self.crypt_key)
        else:
            crypt_path=PathCrypt.xor_path(file_path_without_ext,self.crypt_key)
        
        print("crypt %s => %s"%(file_path_without_ext,crypt_path))
        out_file=os.path.join(self.out_folder_path,crypt_path+file_ext)
        
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
        
    