
/**	add by obf tools start */

static std::string s_obfuscateKey = "abcd";

void FileUtils::setObfuscateKey(const std::string & key)
{
	s_obfuscateKey = key;
}

void FileUtils::setObfNameDictionary(const ValueMap& nameDict)
{
	_obfNameDict = nameDict;
}

void  FileUtils::loadObfNameDictionaryFromFile(const std::string &filename)
{
	const std::string fullPath = fullPathForFilename(filename);
	if (!fullPath.empty())
	{
		ValueMap dict = FileUtils::getInstance()->getValueMapFromFile(fullPath);
		if (!dict.empty())
		{
			setObfNameDictionary(dict);
		}
	}
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

std::string FileUtils::getObfTargetPath(const std::string& filepath) const
{
	if (!s_obfuscateKey.empty()) {
		std::string obfFilepath = s_obfuscateKey + "_" + filepath;
		Data data;
		data.copy((const unsigned char*)(obfFilepath.c_str()), obfFilepath.length());
		std::string crypt = utils::getDataMD5Hash(data);
		auto iter = _obfNameDict.find(crypt);

		if (iter == _obfNameDict.end())
		{
			return crypt.substr(0, 1) + "/" + crypt;
		}
		else
		{
			return iter->second.asString();
		}
	}
	else
	{
		auto iter = _obfNameDict.find(filepath);

		if (iter == _obfNameDict.end())
		{
			return filepath;
		}
		else
		{
			return iter->second.asString();
		}
	}
}


std::string FileUtils::getObfuscatePathAndCheckSub(const std::string& filepath, const std::string& searchPath) const
{
	std::string path;
	std::string obf_file_path;

	//check sub path
	//sub path like [hd,cocosress]
	//file_path a/b.png
	//will ceck hd/a/b.png,cocosress/a/b.png
	for (const auto& subIt : _obfuscateSubPaths)
	{
		obf_file_path = subIt + filepath;
		obf_file_path = getObfTargetPath(obf_file_path);
		path = getFullPathForDirectoryAndFilename(searchPath, obf_file_path);
		if (!path.empty()) {
			return path;
		}
	}

	//check orignal path
	obf_file_path = filepath;
	obf_file_path = getObfTargetPath(obf_file_path);
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
	std::string path;
	std::string obf_file_path= filepath;
	for (const auto& parentIt : _obfuscateParentPaths)
	{
		int pos = obf_file_path.find(parentIt);
		if (pos == 0) {
			obf_file_path = obf_file_path.substr(parentIt.length());
			path = getObfuscatePathAndCheckSub(obf_file_path, searchPath);
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
/**	add by obf tools end */
