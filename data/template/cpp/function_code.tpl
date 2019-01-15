${return_type.to_string()} #slurp
#if $cpp_class
${cpp_class.name}::${name}(#slurp
#else
${name}(#slurp
#end if
## ===== include parameters 
#include os.path.join($tpl_folder_path,"parameter.tpl")
)
{
#include os.path.join($tpl_folder_path,"function_body.tpl")
}

