from cpp_garbage import CppFile

cf=CppFile({
    "head_file":"../data/temp/a.h",
    "source_file":"../data/temp/a.cpp",
    "tpl_folder":"../data/template",
    "namespace":"my",
    "generate_field":2,
    "generate_method":3
})

cf.generate_code()