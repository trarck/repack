#include "c.h"

A::A()
{
    
}

A::~A()
{}

void A::ama(){
    int i=0;
    i+=3;
}



float A::afa(){
    float i=0;
    i+=3;
    return i;
}

namespace foo
{
C::C()
{
    
}

C::~C()
{}

void C::ma(){
    int i=0;
    i+=3;
}

int C::ia()
{
int i=0;
int j=0;
    i+=3;
j*=4;
    return i;
}

float C::fa(){
    float i=0;
    i+=3;
    return i;
}

}

namespace bar
{
D::D()
{
    
}

D::~D()
{}

void D::ma(){
int i=0;
i+=3;
}

int D::ia()
{
int i=0;
int j=0;
    i+=3;
j*=4;
    return i;
}

float D::fa(){
    float i=0;
    i+=3;
    return i;
}

}

int A::aia()
{
int i=0;
int j=0;
    i+=3;
j*=4;
    return i;
}