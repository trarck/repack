# from pbxproj import XcodeProject, PBXProvioningTypes
#
# pbx_project = XcodeProject.load("../data/Unity-iPhone.xcodeproj/project.pbxproj")
# pbx_project.save()


fp = open("../data/temp/t.bin", "w+")
fp.write(chr(12))
fp.write(chr(13))
fp.write(chr(68))
fp.write(chr(129))
fp.write(chr(140))
fp.close()