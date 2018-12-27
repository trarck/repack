from resource.resource_mapping import ResourceMapping
from resource.directory_generator import DirectoryGenerator
import utils;

# dg=DirectoryGenerator(3,[10,6],[15,10],True)
# # dg.generate("../data/temp/gen_dir")
# dirs=dg.generate("../data/temp/gen_dir")
# print len(dirs)
rule=utils.create_rules(None,["ccs-res","hd"])
dir_gen = DirectoryGenerator(3, [10, 6], [15, 10], True)
dirs = dir_gen.generate("D:/c/cocos2d-x/MyGame/res/hd")
res_mapping = ResourceMapping("D:/c/cocos2d-x/MyGame/res/hd", dirs, False, True)
res_mapping.mapping("D:/c/cocos2d-x/MyGame/res_bak/hd",None,True)
res_mapping.save_mapping_data("D:/c/cocos2d-x/MyGame/res/aaa.json", None, True, True)
# res_mapping = ResourceMapping("../data/temp/res_bak",  True)
# res_mapping.mapping(3, 3, 6,"../data/temp/res1",None,True)
# for k, v in res_mapping.map.items():
#     print("%s=>%s" % (k, v))
