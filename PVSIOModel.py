import websocket
import thread
import time
import json
import matplotlib.pyplot as p
from fractions import Fraction
import pickle

data = []
command = ""
iterations = 0
ydisplay = [0]
xdisplay =[0]
#yError=[]
T=200
reference=0.0


i=1
time=0
target=0
cumulTime =0

def convert(s):
    try:
        return int(s)
    except ValueError:
        return float(Fraction(s))

def parseOutput(output):
    s = output.strip("(##)")
    d = dict(item.split(":=") for item in s.split(",")) # Generate dictionary
    return { k.strip():convert(v.strip()) for k, v in d.iteritems()} # Remove whitespace in dictionary

def sendCommand(ws, command, state):
    state['command'] = command
    cmdstate = '{command}((# left_display:={left_display}, step:={step}, timer:={timer} #));'.format(**state);
    d = {"type":"sendCommand", "data":{'command':cmdstate}}
    print "Sending:", d
    ws.send(json.dumps(d))


def pvsCommand(pvstype,pvscmd):

    if(pvstype == "mousedown" or pvstype=="mouseup"):
        if(pvscmd == "smallDown"):
            return "press_dn"
        if(pvscmd == "bigUp"):
            return "press_UP"
        if(pvscmd == "bigDown"):
            return "press_DN"
        if(pvscmd == "smallUp"):
            return "press_up"

    if(pvstype == "click"):
        if(pvscmd == "smallDown"):
            return "click_dn"
        if(pvscmd == "smallUp"):
            return "click_up"
        if(pvscmd == "bigDown"):
            return "click_DN"
        if(pvscmd == "bigUp"):
            return "click_UP"


def on_message(ws, message):
    global command, iterations, xdisplay, yError, ydisplay, T, i, time, target, cumulTime,reference

    print "Message: ", message
    decoded = json.loads(message)
    dtype =  decoded['type']
    
    print 'TYPE:', dtype

    if(dtype == 'processReady'):
        ws.send('{"type":"sendCommand","data":{"command":"'+command+'((# left_display := 0, step := 1, timer := 5 #));"}}')

    if(dtype == 'pvsoutput'):
        print zip(xdisplay, ydisplay)
        print data
        
        result = decoded['data']
        output = parseOutput(result[0])
        print 'Output: ', output

        ldisplay = output['left_display']

        error = float(reference) - ldisplay
        print "Error: ", error
        #yError.append(error)

        iterations +=1
        #i+=1


        if(i<len(data)):

            if(i>0):
                if data[i-1]['im'] == "click": #if previous action was a click, record the current value
                    xdisplay.append(data[i-1]['ts']-time)
                    ydisplay.append(ldisplay)

            print "I:",i

            nextAction = data[i]['im']
            nextButton = data[i]['btn']
            timediff = data[i]['ts']  - time
            print "Time difference: ", timediff 
            print "NextAction: ", nextAction       

            if nextAction == "mousedown":

                #if(iterations == 1): #For the first iteration we already pressed big up
                #    nextAction = "mouseup"

                target = data[i+1]['v']
                print "Target value: ", target
                
                command = pvsCommand(nextAction,nextButton)

                i+=1

            
            if nextAction == "mouseup":            
                print "Target: ", target
                print "Display: ", ldisplay

                xdisplay.append(cumulTime+(iterations*T))
                ydisplay.append(ldisplay)

                if float(target) == float(ldisplay): # reached target value, release_key
                    command = "release_key"
                    i+=1
                    
                    iterations = -1 #take the extra timestep required by release_key into account
                    
                    cumulTime = data[i]['ts']  - time # need to know before the next hold_down starts
                    
                    #Add waiting time
                    xdisplay.append(cumulTime)
                    ydisplay.append(ldisplay)
                #else do nothing, command will stay the same


            if nextAction == "click":
   

                #Add waiting time
                xdisplay.append(data[i]['ts']  - time)
                ydisplay.append(ldisplay)

                i+=1

                command = pvsCommand(nextAction,nextButton)
        
        if iterations>50: # Don't continue beyond 50 button presses
            print "TIMED OUT"
            error = 0

        if(error == 0):
            command = ""
            xdisplay.append(data[i-1]['ts']  - time)
            ydisplay.append(ldisplay)
            
            ws.close()
            

        if(command != ""):
            sendCommand(ws,command,output)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    ws.send('{"type":"startProcess","data":{"fileName":"pvscode/alarisAsenaCC"}}')


#if __name__ == "__main__":
def getDisplay(startTime,endValue,userInput):
    global data, reference, time,command,iterations,ydisplay,xdisplay,i,cumulTime,target

    # Initialize variables    
    iterations = 0
    ydisplay = [0]
    xdisplay =[0]
    i=1
    cumulTime=0

    #Set globals
    data = userInput
    reference = endValue
    time = startTime
    command = pvsCommand(data[0]['im'],data[0]['btn'])

    print command

    if(data[0]['im'] == "mousedown"):
        target = data[1]['v']
        print "Target value: ", target

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8080/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)

    

    ws.on_open = on_open

    ws.run_forever()
    
    return (xdisplay, ydisplay)
