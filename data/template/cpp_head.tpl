/**
 * this file is generate by repack
 */
#ifndef __REPACK_${class_name}_H__
#define __REPACK_${class_name}_H__

#include "cocos2d.h"

${NAMESPACE_BEGIN}

class CC_DLL ${class_name} {
public:
	${class_name}();
	~${class_name}();

	${METHOD_DECLARES}

    ${PROPERTY_DECLARES}
    
};

${NAMESPACE_END}

#endif    // __REPACK_${class_name}_H__
