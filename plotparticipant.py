import json
import matplotlib.pyplot as p
import pickle
import itertools

import operator



time=0
reference = 6.8 
yDisplay = []
yOutput = [0]
yVelocity = [0]
x = [0]

#def most_common(L):
#  groups = itertools.groupby(sorted(L))
#  def _auxfun((item, iterable)):
#    return len(list(iterable)), -L.index(item)
#  return max(groups, key=_auxfun)[0]

def getData():
    users = []
    findcommon = []
    
    f = open('big.json','r')
    d = json.load(f)    

    for x in d['results']['participants']:
        print x['name']
        results = []
        for i in x['chevrons']:
            results.append((i['st'],i['ev'],i['rt']))
        users.append(results)

    return users


user = getData()[2] # get first user

nrPlots = len(user)
print nrPlots

iterations = 0
for y in range(0,10):
#for result in user:
    result = user[y]    
    p.subplot(5,2,y)
    
    #p.subplot(nrPlots/2,2,iterations)
    #iterations += 1

    time = result[0] # take start time as t:=0
    reference = result[1]

    yDisplay = []
    x = [0]
    mouseEvents = 0

    for i in result[2]:
        #print i['btn'], ": ", i['im'], ": ",i['v'],": ", i['ts'] - time
        if "mouse" in i['im']:
            mouseEvents +=1
        
        if i['ts'] - time != 0:    
            x.append(i['ts'] - time)

        yDisplay.append(i['v'])

    print mouseEvents
    if mouseEvents % 2 == 0:
        print "EQUAL"
    else:
        print "NOT EQUAL"
    

    p.plot(x,yDisplay,'r+-', label="User")
    p.plot(x,[reference for i in x],'b', label = "Reference signal")

p.xlabel("Time")
#p.legend()
p.tight_layout() # to prevent clipping of titles and labels         
#p.savefig('participant.pdf',format="pdf") #Only valid for (e)ps:,papertype='A4', orientation='landscape')
p.show()
p.close()




