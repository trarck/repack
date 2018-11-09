
@implementation ${class_name}
##======field init======
#set $length = len($fields)
#if $length > 0
    #for $field in $fields
@synthesize ${field.name};
    #end for
#end if

