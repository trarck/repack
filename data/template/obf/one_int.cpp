
    int ${var_name}=${num[0]};
    do{
        while(true)
        {
            while(${var_name}==${num[0]}){
                ${var_name}=${num[1]};
            }
            
            if(${var_name}!=${num[1]}){
                break;
            }
            ${var_name}=${num[2]};
        }
    }while(${var_name}!=${num[2]});
