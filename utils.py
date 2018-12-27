import os
import shutil
import sys
import random
from rules import *


def in_rules(rel_path, rules):
    ret = False
    path_str = rel_path.replace("\\", "/")
    for rule in rules:
        if re.match(rule, path_str):
            ret = True

    return ret


def convert_rules(rules):
    ret_rules = []
    for rule in rules:
        ret = rule.replace('.', '\\.')
        ret = ret.replace('*', '.*')
        ret = "%s" % ret
        ret_rules.append(ret)

    return ret_rules


def create_rules(include_rules, exclude_rules):
    if include_rules and len(include_rules) > 0:

        include_rules = convert_rules(include_rules)
        rules = []
        for r in include_rules:
            rules.append(RegexpMatchRule(r))
        include_rule = AnyRule(rules)
    else:
        include_rule = None

    if exclude_rules:
        exclude_rules = convert_rules(exclude_rules)
        rules = []
        for r in exclude_rules:
            rules.append(RegexpMatchRule(r))
        exclude_rule = NotRule(AnyRule(rules))
    else:
        exclude_rule = None

    if include_rule and exclude_rule:
        root_rule = AndRule(include_rule, exclude_rule)
    elif include_rule:
        root_rule = include_rule
    else:
        root_rule = exclude_rule

    return root_rule


def copy_files(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        path = os.path.join(src, item)
        if os.path.isfile(path):
            shutil.copy(path, dst)
        if os.path.isdir(path):
            new_dst = os.path.join(dst, item)
            if not os.path.isdir(new_dst):
                os.makedirs(new_dst)
            copy_files(path, new_dst)


def copy_files_with_config(config):
    src_dir = config["from"]
    dst_dir = config["to"]

    include_rules = None
    if "include" in config:
        include_rules = config["include"]
        include_rules = convert_rules(include_rules)

    exclude_rules = None
    if "exclude" in config:
        exclude_rules = config["exclude"]
        exclude_rules = convert_rules(exclude_rules)

    copy_files_with_rules(
        src_dir, src_dir, dst_dir, include_rules, exclude_rules)


def copy_files_with_rules(src_root, src, dst, include=None, exclude=None):
    if os.path.isfile(src):
        if not os.path.exists(dst):
            os.makedirs(dst)
        shutil.copy(src, dst)
        return

    if (include is None) and (exclude is None):
        copy_files(src, dst)
    elif (include is not None):
        # have include
        for name in os.listdir(src):
            abs_path = os.path.join(src, name)
            rel_path = os.path.relpath(abs_path, src_root)
            if os.path.isdir(abs_path):
                sub_dst = os.path.join(dst, name)
                copy_files_with_rules(
                    src_root, abs_path, sub_dst, include=include)
            elif os.path.isfile(abs_path):
                if in_rules(rel_path, include):
                    if not os.path.exists(dst):
                        os.makedirs(dst)

                    shutil.copy(abs_path, dst)
    elif (exclude is not None):
        # have exclude
        for name in os.listdir(src):
            abs_path = os.path.join(src, name)
            rel_path = os.path.relpath(abs_path, src_root)
            if os.path.isdir(abs_path):
                sub_dst = os.path.join(dst, name)
                copy_files_with_rules(
                    src_root, abs_path, sub_dst, exclude=exclude)
            elif os.path.isfile(abs_path):
                if not in_rules(rel_path, exclude):
                    if not os.path.exists(dst):
                        os.makedirs(dst)

                    shutil.copy(abs_path, dst)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    if len(parts) == 1:
        m = sys.modules[__name__]
        m = getattr(m, parts[0])
    else:
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
    return m


def pad(size):
    return ''.join(' ' for _ in range(size))


def merge_dict(a, b):
    c = a.copy()
    c.update(b)
    return c


def generate_key():
    return ''.join(chr(random.randrange(ord('a'), ord('z'))) for _ in range(16))


words = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
words_length = len(words)


def generate_name(min_length=6, max_length=64):
    length = random.randint(min_length, max_length)
    return ''.join(words[random.randint(0, words_length - 1)] for _ in range(length))


def generate_name_first_upper(min_length=6, max_length=64):
    name = generate_name(min_length, max_length)
    return name[0].upper() + name[1:]


def generate_name_first_lower(min_length=6, max_length=64):
    name = generate_name(min_length, max_length)
    return name[0].lower() + name[1:]


def generate_int(max_value=2147483640):
    return random.randint(0, max_value)


def generate_float(max_value=2147483640):
    return random.uniform(0, max_value)


def generate_string(min_length=6, max_length=64):
    return generate_name(min_length, max_length)
