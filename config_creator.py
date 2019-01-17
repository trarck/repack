import traceback
import sys
import json
from argparse import ArgumentParser
from generater import RandomGenerater


class ConfigCreator:
    def __init__(self):
        print ""

    @staticmethod
    def create_crypt_info(key):
        return {
            "key": key,
            "type": "md5",
            "with_ext": False
        }

    def create_project(self, project_name, crypt_key, xcode_project_path, origin_xcode_project_name, xcode_project_name,
                       target_name=None, display_name=None, xxtea_key=None, xxtea_sign=None):

        project_data = {}

        project_data["name"] = project_name
        project_data["resource_path"] = project_name
        project_data["project_path"] = project_name
        project_data["crypt"] = ConfigCreator.create_crypt_info(crypt_key)
        project_data["xcode_project_path"] = xcode_project_path
        project_data["origin_xcode_project_name"] = origin_xcode_project_name
        project_data["xcode_project_name"] = xcode_project_name

        if target_name:
            project_data["target_name"] = target_name
        if display_name:
            project_data["display_name"] = display_name
        if xxtea_key:
            project_data["xxtea_key"] = xxtea_key
        if xxtea_sign:
            project_data["xxtea_sign"] = xxtea_sign

        project_data["gen_cpp_dir"] = RandomGenerater.generate_string(6, 12)
        project_data["gen_objc_dir"] = RandomGenerater.generate_string(6, 12)

        project_data["origin_xcode_project_name"] = project_name
        project_data["xcode_project_name"] = project_name + ".ipa"

        return project_data

    def save_project(self, project_data, out_file_path):
        config_data = {
            "projects": [project_data]
        }
        fp = open(out_file_path, "w+")
        json.dump(config_data, fp)
        fp.close()


def main():
    parser = ArgumentParser()

    parser.add_argument('-o', '--out', dest='out',
                        help="config file out put")

    parser.add_argument('-n', '--name', dest='name',
                        help="project name")

    parser.add_argument('--crypt-key', dest='crypt_key',
                        help="obf key")

    parser.add_argument('--xcode-project-path', dest='xcode_project_path',
                        help="xcode project path")

    parser.add_argument('--origin-xcode-project-name', dest='origin_xcode_project_name',
                        help="origin xcode project name")

    parser.add_argument('--xcode-project-name', dest='xcode_project_name',
                        help="xcode project name")

    parser.add_argument('--target-name', dest='target_name',
                        help="target name")

    parser.add_argument('--display-name', dest='display_name',
                        help="display name")

    parser.add_argument('--xxtea-key', dest='xxtea_key',
                        help="xxtea key")

    parser.add_argument('--xxtea-sign', dest='xxtea_sign',
                        help="xxtea sign")

    args = parser.parse_args()

    target_name = None
    if "target_name" in args:
        target_name = args.target_name

    display_name = None
    if "display_name" in args:
        display_name = args.display_name

    xxtea_key = None
    if "xxtea_key" in args:
        xxtea_key = args.xxtea_key

    xxtea_sign = None
    if "xxtea_sign" in args:
        xxtea_sign = args.xxtea_sign

    config_creator = ConfigCreator()
    project_data = config_creator.create_project(args.name, args.crypt_key, args.xcode_project_path,
                                                 args.origin_xcode_project_name, args.xcode_project_name, target_name,
                                                 display_name, xxtea_key, xxtea_sign)

    config_creator.save_project(project_data, args.out)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
