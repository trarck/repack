from resource.directory_generator import DirectoryGenerator
from resource.resource_mapping import ResourceMapping
import os

# dg=DirectoryGenerator(3,3,6)
# # dg.generate("../data/temp/gen_dir")
# dirs=dg.generate("../data/temp/gen_dir")
# print len(dirs),dirs

res_mapping = ResourceMapping("../data/temp/res_bak", "../data/temp/res1", True)
res_mapping.mapping(3, 3, 6)
