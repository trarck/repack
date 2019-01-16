# -*- coding: utf-8 -*-
import random
from clang import cindex


def get_range_count(name, config, default_min=1):
    """
    取得一个范围内的随机值。
    :param name:
    :param config:
    :param default_min:
    :return:
    """
    if name in config:
        return config[name]

    max_key = "max_" + name
    min_key = "min_" + name

    if max_key in config:
        max_value = config[max_key]

    if min_key in config:
        min_value = config[min_key]
    else:
        min_value = default_min

    if min_value > max_value:
        max_value = min_value
    return random.randint(min_value, max_value)


def get_implement_functions(parser, ruler):
    """
    取得函数,包括普通函数和类的方法。不包含定义在类的内部的方法。
    :param parser:
    :param ruler:
    :return:
    """
    functions = parser.functions
    impl_funcs = []
    for func in functions:
        if func.is_implement:
            if ruler:
                class_name = func.class_name if func.class_name else "*"
                if not ruler.should_skip(class_name, func.name):
                    impl_funcs.append(func)
            else:
                impl_funcs.append(func)
    return impl_funcs


def get_all_implement_functions(parser, ruler):
    """
    所有函数。不论在哪定义的。
    :param parser:
    :param ruler:
    :return:
    """
    impl_funcs = get_implement_functions(parser, ruler)
    for _, cls in parser.parsed_classes.items():
        for func in cls.methods:
            if func.is_implement:
                if ruler:
                    class_name = func.class_name if func.class_name else "*"
                    if not ruler.should_skip(class_name, func.name):
                        impl_funcs.append(func)
                else:
                    impl_funcs.append(func)
    return impl_funcs


def group_functions(functions):
    groups = {}

    for func in functions:
        if func.is_implement:
            if func.cursor.lexical_parent.kind == cindex.CursorKind.NAMESPACE \
                    or func.cursor.lexical_parent.kind == cindex.CursorKind.TRANSLATION_UNIT:
                key = func.cursor.lexical_parent.spelling
                if key in groups:
                    group = groups[key]
                else:
                    group = {
                        "cursor": func.cursor.lexical_parent,
                        "functions": []
                    }
                    groups[key] = group
                group["functions"].append(func)

    return groups


def get_cursor_children_start(cursor):

    if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
        return cursor.extent.start.line, cursor.extent.start.column
    else:
        for c in cursor.get_children():
            return c.extent.start.line, c.extent.start.column
