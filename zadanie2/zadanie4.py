# -*- coding: cp1250 -*-


class Samochod:
    def __init__(self, marka, model, rocznik):
        self.marka = marka
        self.model = model
        self.rocznik = rocznik

    def get_marka(self):
        return self.__marka
    def set_marka(self,marka):
        self.__marka=marka

    def get_model(self):
        return self.__model
    def set_model(self,model):
        self.__model=model

    def get_rocznik(self):
        return self.__rocznik
    def set_rocznik(self,rocznik):
        self.__rocznik=rocznik
    def zasieg(self, bak, spalanie):
        return bak / spalanie *100


class Disel(Samochod):
    def tankuj(self):
        print 'Zatankowano ropą auto: ' + self.marka + ' ' + self.model
    

class Benzynowy(Samochod):
    def tankuj(self):
        print 'Zatankowano benzyną auto: ' + self.marka + ' ' + self.model
    

class Elektryczny(Samochod):
    def zasieg(self, zasiegNaBaterii):
        return zasiegNaBateri
    def naladujBaterie(self):
        print 'Naładowano baterię w aucie: '+ self.marka + ' ' + self.model

class Hybrydowy(Benzynowy, Elektryczny):
    def zasieg(self, bak, spalanie, zasiegNaBaterii):
        return bak / spalanie * 100 + zasiegNaBaterii
    
ford = Benzynowy("Ford", "Mondeo", 2005)
ford.tankuj()
print ford.zasieg(50, 7.0)

toyota = Hybrydowy("Toyota", "Prius", 2014)
toyota.tankuj()
toyota.naladujBaterie()
print toyota.zasieg(40, 4.0, 100)
