void funa()
{
    int i=0;
    int j=2;
    i+=2;
    if (i>j){
        j+=2;
    }

   
    do
    {
      i+=j;
      j+=i;
    }while(i<j);
}

int funb()
{
    int i=0;
    int j=2;
    i+=2;

    if (i>j){
        j+=2;
    }
    
    do
    {
      i+=j;
      j+=i;
    }while(i<j);
    return i;
}

int main()
{
    return 0;
}