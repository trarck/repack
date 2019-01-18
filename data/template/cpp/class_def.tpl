
class ${name} {
## ===== fields 
#set $length = len($fields)
#if $length > 0
public:
    #for $field in $fields
    ${field.to_string()}
    #end for
#end if

#if $implement_construct_destruct
public:
	${name}(){};
	virtual ~${name}(){};
#else
public:
	${name}();
	virtual ~${name}();
#end if
    
## ===== methods 
#set $length = len($methods)
#if $length > 0
public:
    #for $method in $methods
    ${method.get_def_string()}
    #end for
#end if
};
