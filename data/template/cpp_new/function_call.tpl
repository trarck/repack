
##======call code======
    ${name}(#slurp
        ## ===== parameters values
        #set $param_len = len($parameters)
        #if $param_len > 0
            #set $param_index = 0
            #for $param in $parameters
${param.native_type.random_value_stringify()}#slurp
                #if $param_index < $param_len - 1 
,#slurp
                #end if
            #set $param_index = $param_index + 1
            #end for
        #end if
);

