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
#if $return_type.name 
    return ret;
#end if
}

