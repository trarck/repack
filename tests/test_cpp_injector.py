import os
import utils

from garbage_code.cpp_injector import CppInjector, CppFunctionInjector
#
# ci = CppFunctionInjector({
#     "clang_args": [
#         "-x", "c++",
#         "-arch armv7", "-std=c++11" ,"-stdlib=libc++",
#         "-I/usr/include",
#         "-I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1",
#         "-I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/10.0.0/include",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/cocos",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/extensions",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/freetype2/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/curl/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/webp/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/tiff/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/jpeg/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/png/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/websockets/include/ios",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/freetype2/include/ios/freetype2",
#         "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/external/fmod/include",
#         "-DCC_TARGET_OS_IPHONE", "-DCC_ENABLE_CHIPMUNK_INTEGRATION=1", "-DNDEBUG", "-DUSE_FILE32API",
#         "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS12.1.sdk"
#     ],
#     "tpl_folder": "../data/template/obf"
# })
#
# ci.inject("../data/temp/inject/CCSprite3D.cpp", {
#     'out': "../data/temp/inject/b2.cpp"
# })

#
# ci = CppFunctionInjector({
#         "clang_args": ["-x","c++","-ID:/c/cocos2d-x/cocos","-ID:/c/cocos2d-x/external","-ID:/c/cocos2d-x/extensions","-ID:/c/cocos2d-x/external/win32-specific/gles/include/OGLES","-ID:/c/cocos2d-x/external/glfw3/include/win32",
#                        '-ID:/c/cocos2d-x/MyGame/frameworks/cocos2d-x/external/freetype2/include/win10',
#                         '-ID:/c/cocos2d-x/MyGame/frameworks/cocos2d-x/external/freetype2/include/win10/freetype2',
#                         "-ID:/c/cocos2d-x/external/edtaa3func",
#                         "-ID:/c/cocos2d-x/external/tinyxml2",
#                        "-D_WINDOWS","-DWIN32","-D_USRDLL","-D_USEGUIDLL"],
#     "tpl_folder": "../data/template/obf"
# })
#
# ci.inject("../data/temp/inject/CCSprite3D.cpp", {
#     'out': "../data/temp/inject/b2.cpp"
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
    "tpl_dir":"../data/template/obf"
})
#
cpp_injector.inject_files([
    # "D:/c/cocos2d-x/MyGame/frameworks/cocos2d-x/cocos/ui"
    # "D:/c/cocos2d-x/MyGame/frameworks/cocos2d-x/cocos/2d/CCNode.cpp"
    "../data/temp/inject/a"
])
