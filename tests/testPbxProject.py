from pbxproj import XcodeProject, PBXProvioningTypes

pbx_project = XcodeProject.load("../data/Unity-iPhone.xcodeproj/project.pbxproj")
pbx_project.save()