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


def get_children_array_from_cursor(cursor):
    children = []
    for child in cursor.get_children():
        children.append(child)
    return children


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
                    or func.cursor.lexical_parent.kind == cindex.CursorKind.TRANSLATION_UNIT \
                    or func.cursor.lexical_parent.kind == cindex.CursorKind.UNEXPOSED_DECL:

                if func.cursor.lexical_parent.kind == cindex.CursorKind.UNEXPOSED_DECL:
                    key = func.cursor.translation_unit.cursor.spelling
                else:
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
    min_line = -1
    min_column = -1
    current_file = cursor.extent.start.file.name

    if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
        for c in cursor.get_children():
            if c.extent.start.file and c.extent.start.file.name == current_file:
                if min_line == -1:
                    min_line = c.extent.start.line
                    min_column = c.extent.start.column
                else:
                    if min_line > c.extent.start.line:
                        min_line = c.extent.start.line
                        min_column = c.extent.start.column
                    elif min_line == c.extent.start.line:
                        if min_column > c.extent.start.column:
                            min_column = c.extent.start.column
    else:
        check_list = [cursor]
        while len(check_list) > 0:
            p = check_list.pop()
            for c in p.get_children():
                if c.extent.start.file and c.extent.start.file.name == current_file:
                    check_list.append(c)
                    if min_line == -1:
                        min_line = c.extent.start.line
                        min_column = c.extent.start.column
                    else:
                        if min_line > c.extent.start.line:
                            min_line = c.extent.start.line
                            min_column = c.extent.start.column
                        elif min_line == c.extent.start.line:
                            if min_column > c.extent.start.column:
                                min_column = c.extent.start.column

    return min_line, min_column


def get_function_start(cursor):
    # 检查函数是不是定义在extern C中。如果是返回extern C块的开头。
    if cursor.lexical_parent.kind == cindex.CursorKind.UNEXPOSED_DECL:
        return cursor.lexical_parent.extent.start
    else:
        return cursor.extent.start
