import traceback
import sys
import os
import json
from argparse import ArgumentParser
from config_creator import ConfigCreator
from generater import RandomGenerater
import repack


def main():
    work_path = os.getcwd()
    repack_project_path = os.path.dirname(os.path.realpath(__file__))

    parser = ArgumentParser()

    parser.add_argument('-p', '--project', dest='project',
                        help="xcode project file path")

    parser.add_argument('-s', '--scheme', dest='scheme',
                        help="xcode scheme")

    parser.add_argument('-m', '--mode', dest='mode',
                        help="build mod archive or ipa")

    parser.add_argument('-o', '--out', dest='out',
                        help="out put path")

    args = parser.parse_args()

    xcode_project_file_path = args.project

    if not os.path.isabs(xcode_project_file_path):
        xcode_project_file_path = os.path.join(work_path, xcode_project_file_path)

    origin_xcode_project_name = os.path.basename(xcode_project_file_path)
    project_name = os.path.splitext(origin_xcode_project_name, ".xcodeproj")[0]
    xcode_project_path = os.path.dirname(xcode_project_file_path)
    xcode_project_name = project_name + "_obf.xcodeproj"
    crypt_key = RandomGenerater.generate_string(6, 10)

    config_creator = ConfigCreator()

    project_data = config_creator.create_project(project_name, crypt_key, xcode_project_path,
                                                 origin_xcode_project_name, xcode_project_name)

    project_data["build_scheme"] = args.scheme

    resource_dir = os.path.join(repack_project_path, "../resources")
    config_file = os.path.join(resource_dir, project_name, "project.json")
    config_creator.save_project(project_data, config_file)

    # get matrix project

    pos = xcode_project_file_path.find("frameworks/runtime-src") > -1
    if pos:
        src_project = xcode_project_file_path[:pos]
    else:
        raise Exception("not a cocos project")
    out_dir = os.path.join(repack_project_path, "../tempprojects")
    data_dir = os.path.join(repack_project_path, "data")

    step_config_file = os.path.join(repack_project_path, "../steps.json")
    fp = open(step_config_file)
    step_config = json.load(fp)
    fp.close()

    repack.repack_project(src_project, out_dir, resource_dir, data_dir, project_data,
                          step_config, None, None, None, 1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
