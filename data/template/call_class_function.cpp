##======call a class function======
    ${get_full_class_name()} aa;
    aa.${method.name}(#slurp
        ## ===== parameters values
        #set $param_len = len($method.parameters)
        #if $param_len > 0
            #set $param_index = 0
            #for $param in $method.parameters
${generator.generate_value(param.native_type.name)}#slurp
                #if $param_index < $param_len - 1 
,#slurp
                #end if
            #set $param_index = $param_index + 1
            #end for
        #end if
);



