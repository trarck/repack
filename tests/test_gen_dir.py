from resource.directory_generator import DirectoryGenerator
from resource.resource_mapping import ResourceMapping
import os

# dg=DirectoryGenerator(3,[10,6],[15,10],True)
# # dg.generate("../data/temp/gen_dir")
# dirs=dg.generate("../data/temp/gen_dir")
# print len(dirs)
res_mapping = ResourceMapping("D:/c/cocos2d-x/MyGame/res_bak", True)
res_mapping.mapping(3, [10, 6], [15, 10], "D:/c/cocos2d-x/MyGame/res", True)
res_mapping.save_mapping_data("D:/c/cocos2d-x/MyGame/res/mmmaaa.json", "abcd", True, True)
# res_mapping = ResourceMapping("../data/temp/res_bak",  True)
# res_mapping.mapping(3, 3, 6,"../data/temp/res1",None,True)
# for k, v in res_mapping.map.items():
#     print("%s=>%s" % (k, v))
