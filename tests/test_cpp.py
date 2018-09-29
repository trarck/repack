import re
from cpp_garbage_code import CppFile, CppFileInject, NativeFunction, NativeType, CppGarbageCode

# cf=CppFile({
#     "head_file":"../data/temp/a.h",
#     "source_file":"../data/temp/a.cpp",
#     "tpl_folder":"../data/template/cpp",
#     "namespace":"my",
#     "generate_field":2,
#     "generate_method":3
# })
#
# call_str=cf.generate_code()
# print(call_str)

# cf=CppFileInject({
#     "head_file":"../data/temp/cpp/ccGLStateCache.h",
#     "source_file":"../data/temp/cpp/ccGLStateCache.cpp",
#     "tpl_folder":"../data/template/cpp",
#     "namespace":"my",
#     "generate_field":2,
#     "generate_method":3,
#     "max_parameter":4,
#     "call_others":True
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

line = "namespace GL {namespace tt{"
namespace_pos = 0
namespace_name=""
while (True):
    namespace_pos = line.find("namespace", namespace_pos)
    print(namespace_pos)
    if namespace_pos > -1:
        namespace_pos += len("namespace")
        namespace_end_pos = line.find("{", namespace_pos)
        if namespace_end_pos > -1:
            current_namespace = line[namespace_pos:namespace_end_pos].strip()
        else:
            current_namespace = line[namespace_pos:].strip()
        print(current_namespace)
        if namespace_name:
            namespace_name +="::"+current_namespace
        else:
            namespace_name=current_namespace
    else:
        break

print namespace_name
