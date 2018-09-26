
static std::string s_obfuscateKey = "abcd";

void FileUtils::setObfuscateKey(const std::string & key)
{
	s_obfuscateKey = key;
}

void FileUtils::addObfuscateParentPath(const std::string &parentPath, const bool front)
{
	std::string path = parentPath;
	if (!path.empty() && path[path.length() - 1] != '/')
	{
		path += "/";
	}

	if (front) {
		_obfuscateParentPaths.insert(_obfuscateParentPaths.begin(), path);
	}
	else {
		_obfuscateParentPaths.push_back(path);
	}
}

void FileUtils::addObfuscateSubPath(const std::string &subPath, const bool front)
{
	std::string path = subPath;
	if (!path.empty() && path[path.length() - 1] != '/')
	{
		path += "/";
	}

	if (front) {
		_obfuscateSubPaths.insert(_obfuscateSubPaths.begin(), path);
	}
	else {
		_obfuscateSubPaths.push_back(path);
	}
}

std::string FileUtils::getPathHash(const std::string& filepath) const
{
	
	std::string obfFilepath =s_obfuscateKey + "_" + filepath;
	Data data;
	data.copy((const unsigned char*)(obfFilepath.c_str()), obfFilepath.length());
	std::string crypt= utils::getDataMD5Hash(data);
	return crypt.substr(0, 1) + "/" + crypt;
}


std::string FileUtils::getObfuscatePathAndCheckSub(const std::string& filepath, const std::string& searchPath) const
{
    std::string path;
    std::string obf_file_path;
    
    std::string file_ext=getFileExtension(filepath);
    //check sub path
    //sub path like [hd,cocosress]
    //file_path a/b.png
    //will ceck hd/a/b.png,cocosress/a/b.png
    for (const auto& subIt : _obfuscateSubPaths)
    {
        obf_file_path = subIt + filepath;
        obf_file_path = getPathHash(obf_file_path);
        path = getFullPathForDirectoryAndFilename(searchPath, obf_file_path);
        if (!path.empty()) {
            return path;
        }
        
        //check with ext
        obf_file_path+=file_ext;
        path = getFullPathForDirectoryAndFilename(searchPath, obf_file_path);
        if (!path.empty()) {
            return path;
        }
    }
    
    //check orignal path
    obf_file_path = filepath;
    obf_file_path = getPathHash(obf_file_path);
    path = getFullPathForDirectoryAndFilename(searchPath, obf_file_path);
    if (!path.empty()) {
        return path;
    }
    
    //check with ext
    obf_file_path+=file_ext;
    path = getFullPathForDirectoryAndFilename(searchPath, obf_file_path);
    if (!path.empty()) {
        return path;
    }
    
    return "";
}

//remove parent path
//parent path like [src,res]
//file_path a/b.png do noting
//file_path t/src/a/b.png do noting
//file_path src/a/b.png will check a/b.png
//file_path res/a/b.png will check a/b.png
std::string FileUtils::getObfuscatePathCheckParent(const std::string& filepath, const std::string& searchPath) const
{
    if(_obfuscateParentPaths.size()==0){
        return "";
    }
    
    std::string path;
    std::string obf_file_path= filepath;
    std::string file_ext=getFileExtension(filepath);
    
    for (const auto& parentIt : _obfuscateParentPaths)
    {
        int pos = obf_file_path.find(parentIt);
        if (pos == 0) {
            obf_file_path = obf_file_path.substr(parentIt.length());
            path = getObfuscatePathAndCheckSub(obf_file_path, searchPath);
            if (!path.empty()) {
                return path;
            }
            
            //check with ext
            obf_file_path+=file_ext;
            path = getFullPathForDirectoryAndFilename(searchPath, obf_file_path);
            if (!path.empty()) {
                return path;
            }
            
            obf_file_path = filepath;
        }
    }
    return "";
}

std::string FileUtils::getObfuscatePath(const std::string& filepath,const std::string& searchPath) const
{
	//check sub path
	std::string path = getObfuscatePathAndCheckSub(filepath,searchPath);
	
	if (!path.empty()) {
		return path;
	}
	
	return getObfuscatePathCheckParent(filepath,searchPath);
}