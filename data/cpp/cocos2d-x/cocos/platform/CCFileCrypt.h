#ifndef __CC_FILECRYPT_H__
#define __CC_FILECRYPT_H__

#include <string>
#include <vector>
#include <unordered_map>
#include <type_traits>

#include "platform/CCPlatformMacros.h"


NS_CC_BEGIN

class CC_DLL FileCrypt {
public:
	static FileCrypt* FileCrypt::getInstance();
	FileCrypt();
	~FileCrypt();
	void cleanupXXTEAKeyAndSign();
	void setXXTEAKeyAndSign(const char *key, int keyLen, const char *sign, int signLen);
	unsigned char* decrypt(const unsigned char *data, int dataSize, unsigned int* originSize);
protected:
	bool  _xxteaEnabled;
	char* _xxteaKey;
	int   _xxteaKeyLen;
	char* _xxteaSign;
	int   _xxteaSignLen;
};

NS_CC_END

#endif    // __CC_FILECRYPT_H__
