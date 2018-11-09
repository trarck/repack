##===set return value
#if $return_type.name 
    ${return_type.to_string($generator)} ret = ${generator.generate_value($return_type.name)};
#end if
##======call field======
#set $length = len($fields)
#if $length > 0
    #for $field in $fields
    self.${field.name}=${generator.generate_value(field.native_type.name)};
    #end for
#end if
##======call ohters======
#set $length = len($call_others)
#if $length > 0
    #for $func in $call_others
    [self ${func.name}#slurp
        ## ===== parameters values
        #set $param_len = len($func.parameters)
        #if $param_len > 0
            #set $param_index = 0
            #for $param in $func.parameters
                #if $param_index >0
 ${param.name}#slurp
                #end if
:${generator.generate_value(param.native_type.name)}#slurp
            #set $param_index = $param_index + 1
            #end for
        #end if
];
    #end for
#end if
##======base code======
#if $base_code 
    ${base_code}
#end if
##======return======
#if $return_type.name 
    return ret;
#end if
