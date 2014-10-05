import json
import matplotlib
import matplotlib.pyplot as p
from matplotlib.backends.backend_pdf import PdfPages
import pickle
import itertools
import PVSIOModel

import operator

font = {'size' : 5}
matplotlib.rc('font', **font)

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
    
f = open('prototypeResultsChevrons.json','r')
d = json.load(f)    

for a in d:
  for x in a['experiment']:
   if(not end):  
    print "Trial ID: ", x['trialid']

    starttime = x['inputstream'][0]['ts']
    reference = str(x['expectedvalue'])

    if reference == "6.7":  
        yDisplay = [0]
        xDisplay = [0]
        xu = []
        yu = []
        xt = []
        helddown = False

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
                yDisplay.append(i['value'])

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
        

        
        
        axdata = p.subplot2grid((20,20),(px,py),colspan=4,rowspan=3)
            
        p.title("Trial "+ str(x['trialid'])+ ", reference="+str(reference),fontsize=6)    
        axpos = p.subplot2grid((20,20),(3+px,py),colspan=4,rowspan=1)

        px += 5
        if px == 20:
            px = 0
            py += 5

    #    axdata = p.subplot2grid((4,4),(0,0),colspan=4,rowspan=3)
    #    p.title("Trial "+ str(x['trialid'])+ ", reference="+str(reference),fontsize=6)    
    #    axpos = p.subplot2grid((4,4),(3,0),colspan=4)

        [i.set_linewidth(0.1) for i in axdata.spines.itervalues()]
        axdata.plot(xt,[reference for i in xt],'b', label = "Reference signal")
        axdata.plot(xDisplay, yDisplay,'m-', label="Display")
        axdata.set_xticks([])
        
        axpos.set_frame_on(False)
        axpos.tick_params(axis='both', direction='out',top='off',right='off')        
        axpos.set_yticks([-2,-1,0,1,2])
        axpos.set_ylim(-2,2)
        axpos.set_yticklabels(["Big Down","Small Down","Open","Small Up","Big Up"])
        axpos.plot(xu,yu,'g-', label="u(t)")

        #p.show()

        if(plotid > 15):
            #p.tight_layout() # to prevent clipping of titles and labels

            figure = p.gcf() # get current figure
            figure.set_size_inches(11.69, 8.27)
            figure.savefig("prototypeResults.pdf",format="pdf",papertype='a4',dpi=100)
            p.close()
            end = True

