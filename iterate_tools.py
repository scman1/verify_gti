a= [1, 2, 3]
b= [5,6,7,8]
c= [1,2]
print(a)
print(b)
print(c)
print ("chain a b")
import itertools
for x in itertools.chain(a,b):
	print(x)
print ("chain zip c b")	
for x in itertools.chain(*zip(c,b)):
	print(x)
print ("chain zip c (",c, ") cycle b (",b,")")
for x in itertools.chain(*zip(c,itertools.cycle(b))):
	print(x)

