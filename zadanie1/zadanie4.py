# -*- coding: cp1250 -*-
def bezDuplikatow (lista):
    nowaLista = []
    for i in xrange(0,len(lista)):
        powtarzaSie = False
        for j in xrange(0, len(nowaLista)):
            if lista[i] is nowaLista[j]:
                powtarzaSie = True
                break
            else:
                powtarzaSie = False
                continue
        if powtarzaSie == False:
                nowaLista.append(lista[i]) 

    return nowaLista

print bezDuplikatow(['kot','pies','chomik','kot','pies','pies','wydra','okoń'])
