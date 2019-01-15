/**
 * this file is generate by repack
 */
\#ifndef __REPACK_${class_name}_H__
\#define __REPACK_${class_name}_H__
#if $hpp_headers
#for header in $hpp_headers
\#include "${header}"
#end for
#end if 

${class_define}

\#endif // __REPACK_${class_name}_H__