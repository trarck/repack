\#import "${os.path.basename($head_file_path)}"
#for header in $headers
    #set relative = os.path.relpath(header, $search_path)
    #if not '..' in relative
\#import "${relative.replace(os.path.sep, '/')}"
    #else
\#import "${os.path.basename(header)}"
    #end if
#end for
#if $m_headers
#for header in $m_headers
\#import "${header}"
#end for
#end if
