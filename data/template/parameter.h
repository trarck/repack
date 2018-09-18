## ===== parameters 
#set $length = len($parameters)
#if $length > 0
    #set $index = 0
    #for $param in $parameters
        #${param.to_string($generator)}#slurp
        #if $index < $length - 1 
,#slurp
        #end if
        #set $index = $index + 1
    #end for
#end if