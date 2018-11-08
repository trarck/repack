from objc_file_parser import *

# fp=open("../data/temp/objc/UnityAppController.h")
# lines=fp.readlines()
# parser=OjbCHeadFileParser()
# parser.parse(lines)
# print(parser.classes)
# for class_info in parser.classes:
#     print("class:%s,start:%d,end:%d"%(class_info.name,class_info.start_line,class_info.end_line))

#
fp = open("../data/temp/objc/UnityAppController.mm")
lines = fp.readlines()
parser = ObjCSourceFileParser()
parser.parse(lines)

print("======methods=======")
for method_info in parser.methods:
    print("%s::%s,start:%d,end:%d" % (
    method_info.class_name, method_info.name, method_info.start_line, method_info.end_line))
