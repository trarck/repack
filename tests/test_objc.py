import re
import utils

from objc_garbage_code import ObjCFile

of=ObjCFile({
    "head_file":"../data/temp/a.h",
    "source_file":"../data/temp/a.mm",
    "tpl_folder":"../data/template/objc",
    "generate_field":3,
    "generate_method":3,
    "max_parameter":6,
    "call_others":True
})
of.prepare()
call_str=of.generate_code()
print(call_str)
#
# cf = CppFileInject({
#     "head_file": "../data/temp/cpp/CCActionGrid.h",
#     "source_file": "../data/temp/cpp/CCActionGrid.cpp",
#     "tpl_folder": "../data/template/cpp",
#     "namespace": "my",
#     "generate_field": 2,
#     "generate_method": 3,
#     "max_parameter": 4,
#     "call_others": True,
#     "macros": {
#         "NS_CC_BEGIN": "namespace cocos2d {",
#         "NS_CC_END": "}"
#     },
#     "inject_method": {
#         "probability": 100,
#         "class_rule": utils.create_rules(None, ["*DeccelAmplitude"]),
#         "method_rule": utils.create_rules(None, ["update"])
#     }
# })
# cf.prepare()
# cf.inject_code()

# cf=CppFile({
#     "head_file":"../data/temp/b.h",
#     "source_file":"../data/temp/b.cpp",
#     "tpl_folder":"../data/template/cpp",
#     "class_name":"GenerateExecutor",
#     "namespace":"my"
# })
# cf.prepare()
#
# method_code="BB bb;\nbb.a();\nCC cc;\ncc.ma();\n"
# method=NativeFunction("execGeneratedCode",[],NativeType(None),"../data/template/cpp/function.h","../data/template/cpp/function.cpp",method_code)
# cf.native_class.methods.append(method)
# cf.headers=["a.h","b.h","c.h"]
# cf.generate_code()
# call_str=cf.get_class_execute_chain(1)
# print(call_str)

# cpp_code = CppGarbageCode("../data/template/cpp")
# cpp_code.inject_files(["../data/temp/cocos"], {"probability": 100,
#                                                "generate_field_count": 4,
#                                                "generate_method_count": 5,
#                                                "parameter_count": 3})