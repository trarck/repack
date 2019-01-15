
@interface ${name} : NSObject

## ===== fields 
#set $length = len($fields)
#if $length > 0
    #for $field in $fields
${field.to_string()}
    #end for
#end if

## ===== methods 
#set $length = len($methods)
#if $length > 0
    #for $method in $methods
${method.get_def_string()}
    #end for
#end if
@end
