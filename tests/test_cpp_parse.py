from cparser.parser import Parser
from pprint import pprint

parser = Parser({
    "clang_args": [
        "-x", "c++",
        "-arch armv7", "-std=c++11" ,"-stdlib=libc++",
        "-I/usr/include",
        "-I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1",
        "-I/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/10.0.0/include",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/cocos",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/extensions",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/freetype2/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/curl/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/webp/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/tiff/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/jpeg/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/png/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/websockets/include/ios",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/freetype2/include/ios/freetype2",
        "-I/Users/duanhh/workspace/load_pack/tempprojects/test3/frameworks/cocos2d-x/external/external/fmod/include",
        "-DCC_TARGET_OS_IPHONE", "-DCC_ENABLE_CHIPMUNK_INTEGRATION=1", "-DNDEBUG", "-DUSE_FILE32API",
        "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS12.1.sdk"

    ],
    "tpl_folder": "../data/template/obf"
})

ast =parser.get_ast("../data/temp/inject/CCSprite3D.cpp");
pprint(('nodes',ast))
