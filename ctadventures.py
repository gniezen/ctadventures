import json
import matplotlib.pyplot as p
import pickle

#json_data=open("data3.json").read()
#data = json.loads(json_data)

time=0
reference = 6.8 
yDisplay = []
yOutput = [0]
yVelocity = [0]
x = [0]
T=0.22


def getData(val):
    users = []
    
    f = open('big.json','r')
    d = json.load(f)    

    for x in d['results']['participants']:
        for i in x['chevrons']:
            if float(i['ev']) == val:
                users.append(i['rt'])

    return users

def plotResult():
    global x, reference, T

    f = open('actions.bin','rb')
    x2 = pickle.load(f)
    yDisplay2 = pickle.load(f)
    f.close()

    #x = range(0,iterations)
    p.plot(x,yDisplay,'r+-', label="User")
    p.plot([i*1000 for i in x2] ,yDisplay2,'g+-', label="Model")
    p.plot(x,[reference for i in x],'b', label = "Reference signal")
    #p.step(x,yVelocity,'g', label="Velocity")
    p.xlabel("Time")
    p.legend()
    p.show()

for data in getData(6.80):
    #print i

    yDisplay = []
    x = [0]

    time = data[0]['ts'] # take first timestamp as t:=0

    for i in data:
        print i['btn'], ": ", i['im'], ": ",i['v'],": ", i['ts'] - time
        
        if i['ts'] - time != 0:    
            x.append(i['ts'] - time)

        yDisplay.append(i['v'])
    print '\n'

    plotResult()
    #break


