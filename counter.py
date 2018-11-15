j=k=l=0
for i in range(0,250):
    if j>7:
        #add it to the test set
        print (i,j,k,l,"test  %d"%k)
        k+=1
    else:
        #add it to the train set
        print (i,j,k,l,"train %d"%l)
        l+=1
    j+=1
    if j>9:
        j=0
