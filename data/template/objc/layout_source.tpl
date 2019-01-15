
#for header in $headers
    #set relative = os.path.relpath(header, $search_path)
    #if not '..' in relative
\#import "${relative.replace(os.path.sep, '/')}"
    #else
\#import "${os.path.basename(header)}"
    #end if
#end for
#if $source_headers
#for header in $source_headers
\#import "${header}"
#end for
#end if

${class_code}
