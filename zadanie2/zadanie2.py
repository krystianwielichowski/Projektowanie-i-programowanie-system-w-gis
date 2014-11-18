potrawy = []
ceny = []

plik = open("menu.txt", "r")
for linia in plik:
    potrawy.append(linia[0:linia.index(":")])
    ceny.append(float(linia[linia.index(":")+2:len(linia)-2]))


plik.close()

def rachunek(zamowienie):
    cena = 0
    print 'RACHUNEK\n'
    for i in xrange(0,len(zamowienie)):
        for j in xrange(0,len(potrawy)):
            if (zamowienie[i]== potrawy[j]):
                print '{} {}'.format(potrawy[j], ceny[j])
                cena += ceny[j]

    napiwek = cena * 0.2
    razem = cena + napiwek
    
    print '\nCena {}'.format(cena)
    print '\nNapiwek {}'.format(napiwek)
    print 'RAZEM {}'.format(razem)
    return razem

rachunek(["Kotlet", "Ziemniaki", "Frytki"])
