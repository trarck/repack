#if $ctype.name == "NSString*"
@property(nonatomic,copy) ${ctype.to_string()} ${name};
#else
@property(atomic,assign) ${ctype.to_string()} ${name};
#end if

