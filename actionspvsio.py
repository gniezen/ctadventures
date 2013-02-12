import websocket
import thread
import time
import json
import matplotlib.pyplot as p
from fractions import Fraction
import pickle

reference = 6.8

command = ""
iterations = 0
yDisplay = [0]
yOutput = [0]
yVelocity = [0,0]
yError=[]
yError2=[]
T=0.25
x=[0]




def plotResult():
    global x,iterations, yDisplay, yOutput

    p.plot(x,yDisplay,'r+-', label="Input quantity")
    p.plot([reference for i in x],'b', label = "Reference signal")
    p.xlabel("Time step")
    p.legend()
    p.show()
    
    f = open('actions.bin','wb')
    pickle.dump(x,f)
    pickle.dump(yDisplay,f)
    f.close()

def convert(s):
    try:
        return int(s)
    except ValueError:
        #return(s)
        return float(Fraction(s))

def parseOutput(output):
    s = output.strip("(##)")
    d = dict(item.split(":=") for item in s.split(",")) # Generate dictionary
    return { k.strip():convert(v.strip()) for k, v in d.iteritems()} # Remove whitespace in dictionary

def sendCommand(command, state):
    state['command'] = command
    cmdstate = '{command}((# left_display:={left_display}, step:={step}, timer:={timer} #));'.format(**state);
    d = {"type":"sendCommand", "data":{'command':cmdstate}}
    print "Sending:", d
    ws.send(json.dumps(d))

def on_message(ws, message):
    global command, iterations, yDisplay, yOutput, yVelocity, yError, yError2, x, T

    print "Message: ", message
    decoded = json.loads(message)
    dtype =  decoded['type']
    
    print 'TYPE:', dtype


    if(dtype == 'processReady'):
        ws.send('{"type":"sendCommand","data":{"command":"press_UP((# left_display := 0, step := 1, timer := 5 #));"}}')

    if(dtype == 'pvsoutput'):
        iterations += 1
        result = decoded['data']
        output = parseOutput(result[0])
        print 'Output: ', output
        error = reference - output['left_display']
        

        if(command == "release_dn" or command == "release_DN" or command=="release_up" or command=="release_UP"):
            yDisplay.append(output['left_display'])
            x.append(iterations*T)
            print "Displayed: ", yDisplay[-1], " X: ", x

        print "Error: ", error

        yError.append(error)

        if(error > 0):
            if command == "press_DN":
                command = "release_DN"
            elif command == "press_dn":
                command = "release_dn"
            else:
                #if(error > (0.1*reference)):
                if(error > 0.1):
                    if(command == "press_up"):
                        command = "release_up"
                    else:
                        command = "press_UP"
                else:
                    if(command == "press_UP"):
                        command = "release_UP"
                    else:
                        command = "press_up"

        if(error < 0):
            if command == "press_UP":
                command = "release_UP"
            elif command == "press_up":
                command = "release_up"
                
            else:
                #if(error < (0.1*reference)):
                if(error < 0.1):
                    if(command == "press_dn"):
                        command = "release_dn"
                    else:
                        command = "press_DN"
                else:
                    if(command == "press_DN"):
                        command = "release_DN"
                    else:
                        command = "press_dn"                

        if(error == 0):
            command = ""
            yDisplay.append(output['left_display'])
            x.append(iterations*T)
            print "Displayed: ", yDisplay[-1], " X: ", x
            plotResult()

        if(command != ""):
            sendCommand(command,output)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    ws.send('{"type":"startProcess","data":{"fileName":"pvscode/alarisAsenaCC"}}')


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8080/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
