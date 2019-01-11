
##======call code one time======
    static bool ${prefix}_execued=false;
    if(!${prefix}_execued){
        ${prefix}_execued=true;
        ${code}
    }

