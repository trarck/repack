#if $namespace_begin
${namespace_begin}
#end if

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
${field.name}(${generator.generate_value(field.native_type.name)})
    #set $index = $index + 1
    #end for
#end if
{

}

${class_name}::~${class_name}()
{

}

