# -*- coding: cp1250 -*-
def kwadratowa(a,b,c,x):
    return a*x**2 + b*x + c

def miejsca_zerowe(a,b,c):
    
    delta = b**2 - 4*a*c
    if delta > 0:
        x1 = (-b - delta**0.5)/(2*a)
        x2 = (-b + delta**0.5)/(2*a)
        return [x1, x2]
    elif delta == 0:
        
        return [-b/(2*a)]
    else:
        return None


a = 1
b = 2
c = 1

x0 = miejsca_zerowe(a,b,c)

if x0 == None:
    print "Funkcja nie ma miejsc zerowych."
elif len(x0) ==1:
    print "Funkcja ma jedno miejsce zerowe: " + str(x0[0])
else:
    print "Funkcja ma dwa miejsca zerowe: " + str(x0[0]) + " i " + str(x0[1])
    
p1 = -10
p2 = 10

print "Wartości funkcji w prrzedziale od " + str(p1) + " do " + str(p2)
for i in xrange(p1, p2+1):
    print str(i) + " " + str(kwadratowa(a,b,c,i))

