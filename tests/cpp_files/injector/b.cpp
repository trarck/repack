#include "b.h"
#include "a.h"

B::B()
{
    
}


B::~B()
{}

void B::ma(){

int i=0;
A a;
    i+=3;
    a.ma();
}

int B::ia()
{

int i=0;
    int j=0;
    i+=3;
    j*=4;
    return i;
}


float B::fa(){
    
float i=0;
    i+=3;
    
    return i;
}