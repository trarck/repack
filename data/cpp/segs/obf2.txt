	

	if (path.empty()) {
		//use obfuscate path
		std::string obf_file_path = file_path+ resolutionDirectory;
		if (obf_file_path.size() && obf_file_path[obf_file_path.size() - 1] != '/') {
			obf_file_path += '/';
		}
		obf_file_path += file;

		path = getObfuscatePath(obf_file_path, searchPath);
	}
    