import os
import sys
import traceback
import json
import shutil
import base64

from optparse import OptionParser
from pbxproj import XcodeProject

def xor_encrypt(tips,key):
    ltips=len(tips)
    lkey=len(key)
    secret=[]
    num=0
    for each in tips:
        if num>=lkey:
            num=num%lkey
        secret.append( chr( ord(each)^ord(key[num]) ) )
        num+=1

    return base64.b64encode( "".join( secret ).encode() ).decode()


def xor_decrypt(secret,key):

    tips = base64.b64decode( secret.encode() ).decode()

    ltips=len(tips)
    lkey=len(key)
    secret=[]
    num=0
    for each in tips:
        if num>=lkey:
            num=num%lkey

        secret.append( chr( ord(each)^ord(key[num]) ) )
        num+=1

    return "".join( secret )


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
    (opts, args) = parser.parse_args()

    print("=======================================================")
    copy_project(opts.src_project,opts.dest_project)
    rename_project(opts.project_name,opts.package_id)
    
    tips= "1234567"
    key= "owen"
    secret = xor_encrypt(tips,key)
    print( "cipher_text:", secret )

    plaintxt = xor_decrypt( secret, key )
    print( "plain_text:",plaintxt )

# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)