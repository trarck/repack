from cpp_file_parser import *

fp=open("../data/temp/cpp/CCActionGrid.h")
lines=fp.readlines()
parser=CppHeadFileParser({"NS_CC_BEGIN":"namespace cocos2d {","NS_CC_END":"}"})
parser.parse(lines)
print(parser.classes)
for class_info in parser.classes:
    print("class:%s,namespace:%s,start:%d,end:%d"%(class_info.name,class_info.namespace,class_info.start_line,class_info.end_line))

#
# fp = open("../data/temp/cpp/CCFileUtils.cpp")
# lines = fp.readlines()
# parser = CppSourceFileParser({"NS_CC_BEGIN": "namespace cocos2d {", "NS_CC_END": "}"})
# parser.parse(lines)
# print("======namespaces=======")
# for namespace_info in parser.namespaces:
#     print("%s,start:%d,end:%d" % (namespace_info.name, namespace_info.start_line, namespace_info.end_line))
#
# print("======methods=======")
# for method_info in parser.methods:
#     print("%s::%s,start:%d,end:%d" % (
#     method_info.class_name, method_info.name, method_info.start_line, method_info.end_line))
