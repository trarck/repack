## ===== parameters 
#set $length = len($parameters)
#if $length > 0
    #set $index = 0
    #for $param in $parameters
        #if $index >0 
 ${param.name}#slurp
        #end if
:(${param.native_type.to_string($generator)})${param.name}#slurp
        #set $index = $index + 1
    #end for
#end if