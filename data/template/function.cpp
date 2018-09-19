${return_type.to_string($generator)} ${class_name}::${name}(#slurp
## ===== include parameters 
#include os.path.join($generator.tpl_folder_path,"parameter.h")
){
##===set return value
#if $return_type.name 
    ${return_type.to_string($generator)} ret = ${generator.generate_value($return_type.name)};
#end if
##======call field======
#set $length = len($fields)
#if $length > 0
    #for $field in $fields
    ${field.name}=${generator.generate_value(field.native_type.name)};
    #end for
#end if
##======call ohters======
#set $length = len($call_others)
#if $length > 0
    #for $func in $call_others
    ${func.name}(#slurp
        ## ===== parameters values
        #set $param_len = len($func.parameters)
        #if $param_len > 0
            #set $param_index = 0
            #for $param in $func.parameters
${generator.generate_value(param.native_type.name)}#slurp
                #if $param_index < $param_len - 1 
,#slurp
                #end if
            #set $param_index = $param_index + 1
            #end for
        #end if
);
    #end for
#end if
#if $return_type.name 
    return ret;
#end if
}

