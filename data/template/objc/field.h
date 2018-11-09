#if $native_type.name == "NSString*"
@property(nonatomic,copy) ${native_type.to_string($generator)} ${name};
#else
@property(atomic,assign) ${native_type.to_string($generator)} ${name};
#end if

