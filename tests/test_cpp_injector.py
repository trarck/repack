import os
import utils

from garbage_code.cpp_injector import CppInjector,CppFunctionInjector


# ci = CppFunctionInjector({
#     "clang_args": [],
#     "tpl_folder":"../data/template/obf"
# })
#
# ci.inject("../data/temp/inject/a.cpp",{
#     'out':"../data/temp/inject/a2.cpp"
# })

cpp_injector=CppInjector({
    "clang_args": [],
    "tpl_folder":"../data/template/obf"
})

cpp_injector.inject_files([
    ""

])