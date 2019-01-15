#for header in $headers
    #set relative = os.path.relpath(header, $search_path)
    #if not '..' in relative
\#include "${relative.replace(os.path.sep, '/')}"
    #else
\#include "${os.path.basename(header)}"
    #end if
#end for
#if $source_headers
#for header in $source_headers
\#include "${header}"
#end for
#end if

${class_code}

//end ${class_name}