#for header in $headers
    #set relative = os.path.relpath(header, $search_path)
    #if not '..' in relative
\#include "${relative.replace(os.path.sep, '/')}"
    #else
\#include "${os.path.basename(header)}"
    #end if
#end for
#if $cpp_headers
#for header in $cpp_headers
\#include "${header}"
#end for
#end if

${class_code}

//end ${class_name}