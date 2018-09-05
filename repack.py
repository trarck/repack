import os
import sys
import traceback
import json
import shutil
import base64
import random

from argparse import ArgumentParser
from pbxproj import XcodeProject

from path_crypt import PathCrypt
from resource_obfuscator import ResourceObfuscator,CryptInfo
from project import IosProject

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

def set_project(project_root,target_name,package_id,display_name,project_name,product_name,crypt_key):
    print("==> rename project to %s package id %s" % (project_name,package_id))
    ios_project=IosProject(project_root)
    ios_project.rename(target_name,package_id,display_name,project_name,product_name)
    ios_project.set_resource_obfuscate_key(crypt_key)

def obfuscate_resources(res_folder_path,sub_dirs,crypt_info):
    out_folder_path=res_folder_path
    resObf=ResourceObfuscator(res_folder_path,out_folder_path,sub_dirs,crypt_info,False)
    resObf.start()

def main():
    workpath = os.path.dirname(os.path.realpath(__file__))


    parser = ArgumentParser()
    parser.add_argument('-s', '--src-project',dest='src_project',
                      help="src project")

    parser.add_argument('-d', '--dest-project',dest='dest_project',
                      help="dest project")
    
    parser.add_argument('-t','--target-name',dest='target_name',
                      help="new target name")
                      
    parser.add_argument('--project-name',dest='project_name',
                      help="new project name")

                      
    parser.add_argument('--product-name',dest='product_name',
                      help="new product name")

    parser.add_argument('-p', '--package-id',dest='package_id',
                      help="package id")
 
    parser.add_argument('--display-name',dest='display_name',
                      help="display name")
                      
    parser.add_argument('-r', '--resource-dir',dest='resource_dir',
                      help="resource dir")

    parser.add_argument('--sub-dir',dest='sub_dirs',default=[],action='append',
                      help="resource sub dir use for search sub path")
                      
    parser.add_argument('-c', '--crypt-key',dest='crypt_key',
                      help="crypt key")
                      
    parser.add_argument('--crypt-type',dest='crypt_type',default='md5',
                      help="crypt type")
    parser.add_argument('--crypt-out-length',dest='crypt_out_length',default=16,
                      help="crypt out length",type=int)

    parser.add_argument('--crypt-random-position',dest='crypt_random_position',default=8,
                      help="crypt random postion",type=int)
                      
    parser.add_argument('--crypt-with-ext',dest='crypt_with_ext',default=False,
                      help="crypt file path keep ext",type=int, choices=[0, 1])
                      
    args = parser.parse_args()

    print("=======================================================")
    #check crypt key
    if not args.crypt_key :
        #crypt key is none random generate
        args.crypt_key=generate_key()
        print("==> create crypt key %s"%args.crypt_key)

    args.crypt_with_ext=bool(args.crypt_with_ext)
    crypt_info=CryptInfo(args.crypt_key,
                 args.crypt_type,
                 args.crypt_out_length,
                 args.crypt_random_position,
                 args.crypt_with_ext)

    #copy project
    if args.src_project:
        copy_project(args.src_project,args.dest_project)
    
    #set project
    set_project(args.dest_project,
                args.target_name,
                args.package_id,
                args.display_name,
                args.project_name,
                args.product_name,
                args.crypt_key)

    #obfuscate resource
    if args.resource_dir:
        obfuscate_resources(args.resource_dir,args.sub_dirs,crypt_info)
    
    print("======================crypt info========================")
    print("crypt type is %s"%args.crypt_type)
    print("crypt key is %s"%args.crypt_key)
    print("crypt withExt is %s"%args.crypt_with_ext)

# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)