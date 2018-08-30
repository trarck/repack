from pbxproj import XcodeProject
# open the project
project = XcodeProject.load('Unity-iPhone.xcodeproj/project.pbxproj')

# add a file to it, force=false to not add it if it's already in the project
#project.add_file('MyClass.swift', force=False)

# set a Other Linker Flags
project.add_other_ldflags('-ObjC')

# save the project, otherwise your changes won't be picked up by Xcode
project.save()