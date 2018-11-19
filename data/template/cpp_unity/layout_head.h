/**
 * this file is generate by repack
 */
\#ifndef __REPACK_${class_name}_H__
\#define __REPACK_${class_name}_H__
\#include <float.h>
\#include <math.h>
\#include <string.h>
\#include <stdarg.h>
\#include <stdlib.h>
\#include <stdio.h>
\#include <stdint.h>
\#include <time.h>
\#include <string>
\#include <vector>
#if $hpp_headers
#for header in $hpp_headers
\#include "${header}"
#end for
#end if 
