class A(object):
    pass    


def fun(a):
    a.num = 11
    

A.fun = fun

a = A()
a.fun()


