
##======print code======
    static bool _execued_${line_index}=false;
    if(!_execued_${line_index}){
        _execued_${line_index}=true;
		#set $formater=""
		#for $val in $vals
			#if isinstance(val,int)
				#set $formater=$formater+" %d"
			#elif isinstance(val,float)
				#set $formater=$formater+" %f"
			#elif isinstance(val,basestring)
				#set $formater=$formater+" %s"
			#end if
		#end for
		printf("${tag} ${formater}"#slurp
		#for $val in $vals
			#if isinstance(val,int)
,${val}#slurp
			#elif isinstance(val,float)
,${val}f#slurp
			#elif isinstance(val,basestring)
,"${val}"#slurp
			#end if
		#end for
);
    }

