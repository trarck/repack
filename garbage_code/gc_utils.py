# -*- coding: utf-8 -*-


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
                class_name = func.class_name if function.class_name else "*"
                if ruler.should_skip(class_name, func.name):
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
                    class_name = func.class_name if function.class_name else "*"
                    if ruler.should_skip(class_name, func.name):
                        impl_funcs.append(func)
                else:
                    impl_funcs.append(func)
    return impl_funcs
