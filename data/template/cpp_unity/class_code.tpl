
${class_name}::${class_name}()
##======field init======
#set $length = len($fields)
#if $length > 0
    #set $index = 0
    #for $field in $fields
    #if $index==0
    :#slurp
    #else
    ,#slurp
    #end if
${field.name}(${field.random_value_stringify()})
    #set $index = $index + 1
    #end for
#end if
{

}

${class_name}::~${class_name}()
{

}

## ===== methods 
#if $contain_methods
    #for $method in $methods
    ${method.get_code_string()};
    #end for
#end if