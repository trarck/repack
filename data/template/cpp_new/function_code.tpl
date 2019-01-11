${return_type.to_string()} ${class_name}::${name}(#slurp
## ===== include parameters 
#include os.path.join($tpl_folder_path,"parameter.tpl")
)
{
#include os.path.join($tpl_folder_path,"function_body.tpl")
}

