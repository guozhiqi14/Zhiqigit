#-*- coding:utf-8 -*-
def mov(n,A,B,C):
    if n== 1:
        print(A,'->',B)
    else:
        mov(n-1,A,C,B)
        mov(1,A,B,C)
        mov(n-1,C,B,A)

num = input("Input the number of tower：")
mov(int(num),'A','B','C')

 