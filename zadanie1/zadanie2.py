# -*- coding: cp1250 -*-

def Palindrom(napis):
    napis = napis.split()
    napis0 = ""
    for i in xrange(0,len(napis)):
            napis0 = napis0 + napis[i]

    napis = napis0
    napis = napis.lower()
    n = len(napis)
    jestPalindromem = False
    for i in xrange(0,n/2):
        if napis[i] == napis[n-i-1]:
            continue
        else:
            jestPalindromem = False
            return jestPalindromem

    jestPalindromem = True
    return jestPalindromem


print Palindrom("Ikar łapał raki")
print Palindrom("qwerty")
print Palindrom("Ein Esel lese nie")
