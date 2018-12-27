import os
import shutil
from action import Action
import utils
from source_file import SourceFile


class CopyFilesAction(Action):

    def run(self, args):
        src_dir = self.translate_string(self.config["from"])
        dst_dir = self.translate_string(self.config["to"])

        if not os.path.isabs(src_dir):
            src_dir = os.path.join(self.runner.pack_resource_path, src_dir)

        if not os.path.isabs(dst_dir):
            dst_dir = os.path.join(self.runner.project_root_path, dst_dir)

        print("===>copy files from %s to %s" % (src_dir, dst_dir))
        self.config["from"]=src_dir
        self.config["to"]=dst_dir

        utils.copy_files_with_config(self.config)


class DeleteFilesAction(Action):

    def run(self, args):
        if "files" not in self.config:
            return

        for file_path in self.config["files"]:
            file_path = self.translate_string(file_path)
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.runner.project_root_path, file_path)
            print("===>delete file %s" % file_path)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            elif os.path.isfile(file_path):
                os.remove(file_path)


class ModifyFilesAction(Action):

    def run(self, args):
        if "files" not in self.config:
            return

        for modify_config in self.config["files"]:
            file_path = self.translate_string(modify_config["file_path"])
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.runner.project_root_path, file_path)
            source = SourceFile(file_path)
            source.open()
            operation = modify_config["operation"]

            words = None
            if "words" in modify_config:
                words = modify_config["words"]
                words = self.translate_string(words)

            if "words_file" in modify_config:
                words_file_path = self.translate_string(modify_config["words_file"])
                if not os.path.isabs(words_file_path):
                    words_file_path = os.path.join(self.runner.pack_resource_path, words_file_path)
                fp = open(words_file_path)
                words = fp.read()
                fp.close()
                words = self.translate_string(words)

            if operation == "insert":
                source.insert(modify_config["keys"], words)
            elif operation == "insert_before":
                source.insert_before(modify_config["keys"], words)
            elif operation == "replace":
                olds = modify_config["olds"]
                for i in range(len(olds)):
                    olds[i] = self.translate_string(olds[i])

                news = modify_config["news"]
                for i in range(len(news)):
                    news[i] = self.translate_string(news[i])

                source.replace(olds, news)
            elif operation == "search_replace":
                source.search_replace(modify_config["froms"], modify_config["tos"], words)
            elif operation == "search_replace_to_end":
                source.search_replace_to_end(modify_config["froms"], modify_config["tos"], words)
            elif operation == "remove":
                source.remove(modify_config["froms"], modify_config["tos"])
            source.save()


class CopyProjectAction(Action):
    def run(self, args):
        print("copy project from %s to %s" % (self.runner.matrix_project_root_path, self.runner.project_root_path))
        if os.path.exists(self.runner.matrix_project_root_path):
            if os.path.exists(self.runner.project_root_path):
                shutil.rmtree(self.runner.project_root_path)
            shutil.copytree(self.runner.matrix_project_root_path, self.runner.project_root_path, True)
        else:
            print("copy project error no %s folder " % self.runner.matrix_project_root_path)