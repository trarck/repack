
\#include<string>
class ${name} {
## ===== fields 
#set $length = len($fields)
#if $length > 0
public:
    #for $field in $fields
    ${field.to_string()};
    #end for
#end if

public:
	${name}();
	virtual ~${name}();

## ===== methods 
#set $length = len($methods)
#if $length > 0
public:
    #for $method in $methods
    ${method.get_def_string()}
    #end for
#end if
};