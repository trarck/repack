
@implementation ${name}

##======field init======
#set $length = len($fields)
#if $length > 0
    #for $field in $fields
@synthesize ${field.name};
    #end for
#end if

## ===== methods 
#if $contain_methods
    #for $method in $methods
${method.get_code_string()}
    #end for
#end if

@end
