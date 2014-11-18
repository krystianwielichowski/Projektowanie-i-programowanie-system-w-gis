from math import sqrt
class zespolona:
    def get_r(self):
        return self.__r
    def set_r(self,r):
        self.__r=r
    def get_u(self):
        return self.__u
    def set_u(self,u):
        self.__u=u

    def dodaj(self, r1, u1):
        return [self.r+r1, self.u+u1]

    def odejmij(self, r1, u1):
        return [self.r-r1, self.u-u1]
    
    def modul(self):
        return sqrt(self.r**2 + self.u**2)
    
    def wyswietl(self):
        return str(self.r)+ ' + i' + str(self.u)
    



z1 = zespolona()
z1.r = 2
z1.u = 2

print z1.dodaj(5,6)
print z1.modul()

