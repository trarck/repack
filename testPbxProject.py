import os
from source_file import SourceFile
sf=SourceFile("data/temp/t.txt")
sf.open()
sf.replace_after(["dd","bb"],["bb"],"cccc")
sf.save()