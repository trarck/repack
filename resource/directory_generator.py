import random
import os
from generater import RandomGenerater


class DirInfo:

    def __init__(self, have_children, name=None):
        self.name = name if name is not None else RandomGenerater.generate_words(1, 3)
        self.level = 0
        self.parent = None
        self.have_children = have_children
        if have_children:
            self.children = []
        else:
            self.children = None

    def add_child(self, child):
        if self.children is not None:
            child.parent = self
            child.level = self.level + 1
            self.children.append(child)

    def add_to(self, parent):
        parent.add_child(self)

    @property
    def fullname(self):
        names = []
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        names.reverse()
        names.append(self.name)
        return '/'.join(names)


class DirectoryGenerator:

    def __init__(self, max_level, min_dir_count, max_dir_count):
        # dir deep
        self.max_level = max_level
        self.min_dir_count = min_dir_count
        self.max_dir_count = max_dir_count
        self.have_sub_dir_probability = 60
        self.root_dir = DirInfo(True, RandomGenerater.generate_words(1, 1))
        self.dirs = []

    def _generate_children(self, parent_dir):
        sub_count = random.randint(self.min_dir_count, self.max_dir_count)
        for _ in range(sub_count):
            sub_dir = DirInfo(random.randint(0, 100) <= self.have_sub_dir_probability)
            parent_dir.add_child(sub_dir)

    def generate_info(self):
        dir_stack = []
        dir_stack.append(self.root_dir)
        self.dirs = []
        while len(dir_stack) > 0:
            dir_info = dir_stack.pop()
            self.dirs.append(dir_info.fullname)
            if dir_info.have_children and dir_info.level < self.max_level:
                self._generate_children(dir_info)
                for child in dir_info.children:
                    if child.have_children:
                        dir_stack.append(child)

    def show(self):
        for dir_path in self.dirs:
            print dir_path

    def create_dirs(self, out_path):
        for dir_path in self.dirs:
            os.makedirs(os.path.join(out_path, dir_path))

    def generate(self, out_path=None):
        self.generate_info()
        self.show()
        if out_path:
            self.create_dirs(out_path)
        return self.dirs
