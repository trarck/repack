from cpp_garbage_code import CppFile,CppFileInject

# cf=CppFile({
#     "head_file":"../data/temp/a.h",
#     "source_file":"../data/temp/a.cpp",
#     "tpl_folder":"../data/template",
#     "namespace":"my",
#     "generate_field":2,
#     "generate_method":3
# })
#
# cf.generate_code()

cf=CppFileInject({
    "head_file":"../data/temp/cpp/CCCamera.h",
    "source_file":"../data/temp/cpp/CCCamera.cpp",
    "tpl_folder":"../data/template",
    "namespace":"my",
    "generate_field":2,
    "generate_method":3,
    "max_parameter":4,
    "call_others":True
})
cf.inject_code()