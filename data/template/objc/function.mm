-(${return_type.to_string($generator)})${name}#slurp
## ===== include parameters 
#include os.path.join($generator.tpl_folder_path,"parameter.h")

{
#include os.path.join($generator.tpl_folder_path,"function_body.mm")
}

