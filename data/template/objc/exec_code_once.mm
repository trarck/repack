
##======call code one time======
    static bool objc_${prefix}_execued=false;
    if(!objc_${prefix}_execued){
        objc_${prefix}_execued=true;
        ${code}
    }

