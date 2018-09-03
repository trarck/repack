import os
import sys
import traceback
import json
import shutil
import base64
import random

from optparse import OptionParser
from pbxproj import XcodeProject

from path_crypt import PathCrypt
from resource_obfuscator import ResourceObfuscator

def generate_key():
    return ''.join(chr(random.randrange(ord('a'),ord('z'))) for _ in range(16))

def copy_project(src_folder_path,dst_folder_path):
    print("==> copy project from %s to %s" % (src_folder_path,dst_folder_path))
    if os.path.exists(src_folder_path):
        if os.path.exists(dst_folder_path):
            shutil.rmtree(dst_folder_path)
        shutil.copytree(src_folder_path, dst_folder_path)
    else:
        print("copy project error no %s folder " % src_folder_path)

def rename_project(new_project_name,package_id):
    print("==> rename project to %s package id %s" % (new_project_name,package_id))

    
def rename_resources(res_folder_path,crypt_key,crypt_type):
    out_folder_path=res_folder_path
    resObf=ResourceObfuscator(res_folder_path,out_folder_path,crypt_key,crypt_type,False)
    resObf.start()

def main():
    workpath = os.path.dirname(os.path.realpath(__file__))


    parser = OptionParser()
    parser.add_option('-s', '--src-project',dest='src_project',
                      help="src project")

    parser.add_option('-d', '--dest-project',dest='dest_project',
                      help="dest project")
                      
    parser.add_option('-n', '--project-name',dest='project_name',
                      help="new project name")

    parser.add_option('-p', '--package-id',dest='package_id',
                      help="package id")
                      
    parser.add_option('-r', '--resource-dir',dest='resource_dir',
                      help="resource dir")
    parser.add_option('-c', '--crypt-key',dest='crypt_key',
                      help="crypt key")
                      
    parser.add_option('--crypt-type',dest='crypt_type',default="md5",
                      help="crypt type")
    (opts, args) = parser.parse_args()

    print("=======================================================")
    #check crypt key
    if not opts.crypt_key :
        #crypt key is none random generate
        opts.crypt_key=generate_key()
        print("==> create crypt key %s"%opts.crypt_key)
        
    copy_project(opts.src_project,opts.dest_project)
    rename_project(opts.project_name,opts.package_id)

    rename_resources(opts.resource_dir,opts.crypt_key,opts.crypt_type)
    
    print("======================crypt info========================")
    print("crypt type is %s"%opts.crypt_type)
    print("crypt key is %s"%opts.crypt_key)
# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)