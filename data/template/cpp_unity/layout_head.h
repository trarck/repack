/**
 * this file is generate by repack
 */
\#ifndef __REPACK_${class_name}_H__
\#define __REPACK_${class_name}_H__
\#include "cocos2d.h"
#if $hpp_headers
#for header in $hpp_headers
\#include "${header}"
#end for
#end if 
