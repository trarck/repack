import os
import utils

from garbage_code.cpp_injector import CppInjector,CppFunctionInjector


# ci = CppFunctionInjector({
#     "clang_args": [],
#     "tpl_folder":"../data/template/obf"
# })
#
# ci.inject("../data/temp/inject/b.cpp",{
#     'out':"../data/temp/inject/b2.cpp"
# })


cpp_injector=CppInjector({
    "clang_args": ["-x","c++","-ID:/c/cocos2d-x/cocos","-ID:/c/cocos2d-x/external","-ID:/c/cocos2d-x/extensions","-ID:/c/cocos2d-x/external/win32-specific/gles/include/OGLES","-ID:/c/cocos2d-x/external/glfw3/include/win32",
                   '-ID:/c/cocos2d-x/MyGame/frameworks/cocos2d-x/external/freetype2/include/win10',
                    '-ID:/c/cocos2d-x/MyGame/frameworks/cocos2d-x/external/freetype2/include/win10/freetype2',
                    "-ID:/c/cocos2d-x/external/edtaa3func",
                    "-ID:/c/cocos2d-x/external/tinyxml2",
                   "-D_WINDOWS","-DWIN32","-D_USRDLL","-D_USEGUIDLL"],
    "probability": 100,
    # "exclude": [
    #     "*CCAction*", "*CCAnim*", "*CCComp*", "*CCDraw*"
    # ],
    "tpl_folder":"../data/template/obf"

})

cpp_injector.inject_files([
    "D://c//cocos2d-x//MyGame//frameworks//cocos2d-x//cocos//ui"
    # "D://c//cocos2d-x//MyGame//frameworks//cocos2d-x//cocos//2d/CCNode.cpp"
    # "../data/temp/inject/a"
])