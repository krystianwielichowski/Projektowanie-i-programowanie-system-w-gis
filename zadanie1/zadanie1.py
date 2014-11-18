def FizzBuzz(n):
    for i in xrange(1,n):
        if i % 3 == 0:
            if i % 5 == 0:
                print "Fizz Buzz",
            else:
                print "Fizz",
        else:
            print i,
FizzBuzz(16)
