from cpp_garbage_code import CppFile,CppFileInject,NativeFunction,NativeType

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
#     "head_file":"../data/temp/cpp/CCCamera.h",
#     "source_file":"../data/temp/cpp/CCCamera.cpp",
#     "tpl_folder":"../data/template/cpp",
#     "namespace":"my",
#     "generate_field":2,
#     "generate_method":3,
#     "max_parameter":4,
#     "call_others":True
# })
# cf.inject_code()

cf=CppFile({
    "head_file":"../data/temp/b.h",
    "source_file":"../data/temp/b.cpp",
    "tpl_folder":"../data/template/cpp",
    "class_name":"GenerateExecutor",
    "namespace":"my"
})
cf.prepare()

method_code="BB bb;\nbb.a();\nCC cc;\ncc.ma();\n"
method=NativeFunction("execGeneratedCode",[],NativeType(None),"../data/template/cpp/function.h","../data/template/cpp/function.cpp",method_code)
cf.native_class.methods.append(method)
cf.headers=["a.h","b.h","c.h"]
cf.generate_code()
call_str=cf.get_class_execute_chain(1)
print(call_str)