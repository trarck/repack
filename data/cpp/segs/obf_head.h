
/**add by obf tools start*/
	std::vector<std::string> _obfuscateParentPaths;
	std::vector<std::string> _obfuscateSubPaths;
	ValueMap _obfNameDict;
public:
	static void setObfuscateKey(const std::string & key);
	void addObfuscateParentPath(const std::string & path, const bool front = false);
	void addObfuscateSubPath(const std::string & path, const bool front = false);
	void setObfNameDictionary(const ValueMap& nameDict);
	void loadObfNameDictionaryFromFile(const std::string &filename);
	std::string getObfTargetPath(const std::string& filepath) const;
	std::string getObfuscatePathAndCheckSub(const std::string& filepath, const std::string& searchPath) const;
	std::string getObfuscatePathCheckParent(const std::string& filepath, const std::string& searchPath) const;
	std::string getObfuscatePath(const std::string& filepath,const std::string& searchPath) const;
	
protected:
	/**add by obf tools end*/
