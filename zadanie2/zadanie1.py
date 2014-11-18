plik = open("text.txt", "r");
dane = [];
slowa = [];
for linia in plik:
    dane.append(linia);
    for slowo in linia.split():
         slowa.append(slowo);
plik.close()


zbiorSlow = set(slowa);


slowaBezPowt = [];
for element in zbiorSlow:
    slowaBezPowt.append(element);


iloscSlow = [];
for slowo in slowaBezPowt:
    iloscSlow.append(slowa.count(slowo));


plik2 = open("statystyki.txt","w")

for i in xrange(0, len(iloscSlow)):
    plik2.writelines(slowaBezPowt[i] + ": " + str(iloscSlow[i]) + "\n");

plik2.close
