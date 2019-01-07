import os
import shutil
from action import Action
import subprocess


class ShellAction(Action):

    def run(self, args):
        config = self.config

        shell_args = []

        cmd = self.translate_string(config["cmd"])
        shell_args.append(cmd)

        if "args" in config:
            for arg in config["args"]:
                shell_args.append(self.translate_string(arg))

        if args:
            for arg in args:
                shell_args.append(self.translate_string(arg))

        process = subprocess.Popen(shell_args, shell=True)
        output, err = process.communicate()
        print output, err
