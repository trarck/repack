
    do{
        while(true)
        {
            while(${var_name}<${num[1]}){
                ${var_name}=${num[2]};
            }
            
            if(${var_name}>${num[4]}){
                break;
            }
            ${var_name}=${num[5]};
        }
    }while(${var_name}<${num[3]});

