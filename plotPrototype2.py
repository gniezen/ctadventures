import json
import matplotlib
import matplotlib.pyplot as p
from matplotlib.backends.backend_pdf import PdfPages
import pickle
import itertools
import PVSIOModel
import numpy
import sys

import operator
import prettyplotlib as ppl

#font = {'size' : 20}
#matplotlib.rc('font', **font)

if len(sys.argv) > 1:
    ref = float(sys.argv[1])
else:
    ref = 56.7

def getKey(key):

    if(key == "4"): #bigUp
        return 2
    if(key == "5"): #smallUp
        return 1
    if(key == "6"): #smallDown
        return -1
    if(key == "X"): #bigDown
        return -2 

#pp = PdfPages('prototypeResults.pdf')
plotid=0
end = False

px =0
py =0

overshoot = 0
over = False
maxcrossings = 0

with ppl.pretty:
    fig = p.figure()
    #ax = fig.add_axes([0,0,1,1])
    ax = fig.add_subplot(111)
    
f = open('prototypeResultsChevrons.json','r')
d = json.load(f)    

for a in d:
  for x in a['experiment']:
   if(not end):  
    print "Trial ID: ", x['trialid']

    starttime = x['inputstream'][0]['ts']
    reference = str(x['expectedvalue'])

    if reference == str(ref):  
        yDisplay = [0]
        xDisplay = [0]
        xu = []
        yu = []
        xt = []
        helddown = False
        over = False
        crossings = 0

        for i in x['inputstream']:

            time = (i['ts'] - starttime)/1000.0
            xt.append(time)            
            
            if i['type'] == 'keydown':
                xu.append(time)
                yu.append(0)            
                xu.append(time)
                yu.append(getKey(i['key']))   
            
            if i['type'] == 'keyhelddown':  
                helddown = True
        
            if i['type'] == 'ValueChanged':

                if(not helddown):
                    xDisplay.append(time)
                    yDisplay.append(yDisplay[-1])    
                xDisplay.append(time)
                yDisplay.append(float(i['value']))
                
                if(float(i['value']) > float(ref)):
                    over = True
                
                if( ((yDisplay[-2] > ref) and (yDisplay[-1] < ref))
                    or ((yDisplay[-2] < ref) and (yDisplay[-1] > ref)) ):
                        print "yDisplay -2 : ", yDisplay[-2]
                        print "i value: ", yDisplay[-1]
                        print " float ref ", ref
                        crossings +=1 

            if i['type'] == 'keyup':
                xu.append(time)
                yu.append(getKey(i['key']))   
                xu.append(time)
                yu.append(0)
                helddown = False        


        print plotid
        #p.subplot(5,4,plotid)
        
        plotid+=1

        print px
        print py  

        if over:
            overshoot +=1  
        
        if crossings > maxcrossings:
            maxcrossings = crossings

        
        
#        axdata = p.subplot2grid((20,20),(px,py),colspan=4,rowspan=3)
            
        #p.title("Trial "+ str(x['trialid'])+ ", reference="+str(reference),fontsize=6)    
#        axpos = p.subplot2grid((20,20),(3+px,py),colspan=4,rowspan=1)

#        px += 5
#        if px == 20:
#            px = 0
#            py += 5

    #    axdata = p.subplot2grid((4,4),(0,0),colspan=4,rowspan=3)
    #    p.title("Trial "+ str(x['trialid'])+ ", reference="+str(reference),fontsize=6)    
    #    axpos = p.subplot2grid((4,4),(3,0),colspan=4)

        

        #[i.set_linewidth(0.1) for i in p.spines.itervalues()]
        ppl.plot(ax,xt,[reference for i in xt],'b')
        ppl.plot(ax,xDisplay, yDisplay,c=numpy.random.rand(3,),alpha=0.7, label=str(plotid))
        #p.xticks([])
        #ppl.legend(ax, loc='lower right', ncol=5)
        

        #p.show()

        #if(plotid > 30):
            #p.tight_layout() # to prevent clipping of titles and labels

print "Max. crossings: " + str(maxcrossings)
p.text(0.7,0.9,"Overshoot = "+str(overshoot),transform = ax.transAxes) 
p.title("Reference = "+ str(ref)+ " (" + str(plotid) + " trials)")           
#figure = p.gcf() # get current figure
fig.set_size_inches(11.69, 8.27)

fig.savefig("proto/prototypeResults"+str(ref)+".pdf",format="pdf",papertype='a4',dpi=100)
p.close()
end = True

