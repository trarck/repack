
##======call code======
[#slurp
#if $class_inst
${class_inst} #slurp
#else
self #slurp
#end if 
${name}#slurp
## ===== parameters values
#set $param_len = len($parameters)
#if $param_len > 0
    #set $param_index = 0
    #for $param in $parameters
        #if $param_index >0
 ${param.prev}#slurp
        #end if
:${param.ctype.random_value_stringify()}#slurp
    #set $param_index = $param_index + 1
    #end for
#end if
];

