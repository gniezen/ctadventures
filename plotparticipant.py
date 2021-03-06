import json
import matplotlib
import matplotlib.pyplot as p
from matplotlib.backends.backend_pdf import PdfPages
import pickle
import itertools
import PVSIOModel

import operator

time=0
yDisplay = []
yOutput = [0]
yVelocity = [0]
x = [0]

font = {'size' : 5}
matplotlib.rc('font', **font)

def getData():
    users = []
    findcommon = []
    
    f = open('big.json','r')
    d = json.load(f)    

    for x in d['results']['participants']:
        print x['name']
        results = []
        for i in x['chevrons']:
            
            # Use only mousedown,mouseup pairs
            equal = True
            mouseDown = False
            for val in i['rt']:
                if mouseDown:
                    if "mouseup" in val['im']: # if we have a mouse down, the next event must be a mouseup
                        mouseDown = False
                    else:
                        equal = False
                        break
                if "mousedown" in val['im']:
                    mouseDown = True
            if equal:
                print "Equal, adding.."
                results.append((i['st'],i['ev'],i['rt']))
            else:
                print "Not equal, discarding.."

        users.append(results)

    return users



users = getData()

for iteruser in range(0,len(users)):
#for iteruser in range(0,1):

    user = users[iteruser] 
    pp = PdfPages('pplots/participant'+str(iteruser)+'.pdf')

    nrPlots = len(user)
    print "Number of plots: ", nrPlots

    if(nrPlots == 100):
        iterz = 6
    else:
        iterz = (nrPlots/20)+2

    iteration= -1

    for z in range(1,iterz):
        p.clf()
        for y in range(0,20):
            iteration +=1

            if iteration >= len(user):
                break

            result = user[iteration]    
            p.subplot(5,4,y)
            

            time = result[0] # take start time as t:=0
            reference = result[1]

            yDisplay = []
            x = [0]

            for i in result[2]:
                #print i['btn'], ": ", i['im'], ": ",i['v'],": ", i['ts'] - time
                
                if i['ts'] - time != 0:    
                    x.append(i['ts'] - time)

                yDisplay.append(i['v'])

            (xpvsdisplay,ypvsdisplay) = PVSIOModel.getDisplay(time,reference,result[2])
            
            p.title("User "+ str(iteruser)+ ", reference="+str(result[1]),fontsize=6)
            
            try:
                p.plot(x,yDisplay,'r+-', label="User")
            except ValueError, e:
                p.text(0.5, 0.5,'Unable to plot',horizontalalignment='center',verticalalignment='center')
                print e

            p.plot(x,[reference for i in x],'m', label = "Reference signal")

            p.plot(xpvsdisplay, ypvsdisplay,'g-', label="PVSio model")
            p.grid(b=True, which='major', color='b', linestyle='-')
            p.grid(b=True, which='minor', color='y', linestyle='--')
            
            #p.show() ##
        
        p.tight_layout() # to prevent clipping of titles and labels

        figure = p.gcf() # get current figure
        figure.set_size_inches(11.69, 8.27)
        figure.savefig(pp,format="pdf",papertype='a4',dpi=100)
        #p.show()
        p.close()

    pp.close()


