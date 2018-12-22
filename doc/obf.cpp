#include <stdio.h>
//不会被优化掉。
int funWhileEndless()
{
	int i=0;
	
	do
	{
		i+=2;
		i-=3;
		if(i>5){
			i+=4;
		}
	}while(i<13);//死循环

	return i;
}

//不会被优化掉。使用参数
int funParameter(int j)
{
	int i=0;
	
	do
	{
		i+=j;
		if(i>5){//部分满足
			i+=4;
		}
	}while(i<13);

	return i;
}

//简单嵌套会被优化
int simple(int j)
{
	int i=0;
	if(i>0){
		
		do{
			i+=2;
			
			if(i>10){
				
				do{
					
					j=0;
				}while(i<10);
			}
		}while(i<20);
	}

	return i;
}

//使用while和if来构建一个复杂的运行路径
int complex1()
{
	int i=-111;
	int j=33;
	do
	{
		while(true)
		{
			while(i==-111)
			{
				printf("%d",i);
				if(j>10){
					i=22222;
				}else{
					i=18099;
				}
			}
			if(i!=22222){
				break;
			}
			i=18099;
		}
	}while(i!=18099);

	return i;
}

//使用一个变量。
void complex2()
{
    int i=1;
    do{
        while(true)
        {
            while(i==1){
                i=2;
            }
            
            if(i!=2){
                break;
            }
            i=3;
        }
        
    }while(i!=3);
}

//#更多的嵌套
void complex3()
{
    int k=1;
    do{
        while(true)
        {
            while(k==1){ 
                k=2;
                while(true)
                {
                    while(k==2){
                        k=3;
                    }
                    
                    if(k!=3){
                        break;
                    }
                    k=4;
                }
            }
            
            if(k!=2){
                break;
            }
            k=5;
        }
        
    }while(k!=5);
}

//使用float
void complex4()
{
    float i=1;
    do{
        while(true)
        {
            while(i<2){
                i=3;
            }
            
            if(i>5){
                break;
            }
            i=6;
        }
        
    }while(i<4);
}

int main()
{
	printf("%d",complex1());
	return 0;
}