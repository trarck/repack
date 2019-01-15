
##===set return value
#if not $return_type.is_void() 
    ${return_type.to_string()} ret = ${return_type.random_value_stringify()};
#end if
##======call field======
#if $cpp_class
    #set $length = len($cpp_class.fields)
    #if $length > 0
        #for $field in $cpp_class.fields
        ${field.name}=${field.ctype.random_value_stringify()};
        #end for
    #end if
#end if
##======call ohters======
#set $length = len($calls)
#if $length > 0
    #for $func in $calls
    ${func.name}(#slurp
        ## ===== parameters values
        #set $param_len = len($func.parameters)
        #if $param_len > 0
            #set $param_index = 0
            #for $param in $func.parameters
${param.ctype.random_value_stringify()}#slurp
                #if $param_index < $param_len - 1 
,#slurp
                #end if
            #set $param_index = $param_index + 1
            #end for
        #end if
);
    #end for
#end if
##======base code======
#if $base_code 
    ${base_code}
#end if
##======return======
#if not $return_type.is_void()
    return ret;
#end if

