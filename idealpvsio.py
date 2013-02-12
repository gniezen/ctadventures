import websocket
import thread
import time
import json
import matplotlib.pyplot as p
from fractions import Fraction
import pickle

reference = 6.8
positionGain = 20.0

command = ""
iterations = 0
yDisplay = [0]
yOutput = [0]
yVelocity = [0,0]
yError=[]
yError2=[]
T=0.25




def plotResult():
    global iterations, yDisplay, yOutput

    x = range(0,iterations+1)
    p.plot(x,yDisplay,'r+-', label="Input quantity")
    p.plot([reference for i in x],'b', label = "Reference signal")
    p.step(x,yVelocity,'m', label="Velocity")
    #p.plot(x,yError,'c', label="Error")
    #p.plot(x,yError2,'m', label="Error2")
    #p.step(x,yOutput,'c-', label="Output quantity")
    p.xlabel("Time step")
    p.legend()
    p.show()
    
    f = open('ideal.bin','wb')
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
    global command, iterations, yDisplay, yOutput, yVelocity, yError, yError2

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
        yDisplay.append(output['left_display'])
        print "Error: ", error

        if(iterations > 1):
            yVelocity.append((yDisplay[-1] - yDisplay[-2]) / T)


        error2 = positionGain * error - yVelocity[-1]
        yError.append(error)
        yError2.append(error2)

        if(error > 0):
            if command == "press_DN":
                command = "release_DN"
                yOutput.append(yOutput[-1])
            elif command == "press_dn":
                command = "release_dn"
                yOutput.append(yOutput[-1])
            else:
                #if(error > (0.1*reference)):
                if(error > 1.0):
                    command = "press_UP"
                    yOutput.append(200)
                else:
                    command = "press_up"
                    yOutput.append(100)

        if(error < 0):
            if command == "press_UP":
                command = "release_UP"
                yOutput.append(yOutput[-1])
            elif command == "press_up":
                command = "release_up"
                yOutput.append(yOutput[-1])
            else:
                #if(error < (0.1*reference)):
                if(error < 1.0):
                    command = "press_DN"
                    yOutput.append(-200)
                else:
                    command = "press_dn"                
                    yOutput.append(-100)

        if(error == 0):
            command = ""
            plotResult()

        if(command != ""):
            sendCommand(command,output)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
#    def run(*args):
#        for i in range(3):
#            time.sleep(1)
#            ws.send("Hello %d" % i)
#        time.sleep(1)
#        ws.close()
#        print "thread terminating..."
#    thread.start_new_thread(run, ())
    ws.send('{"type":"startProcess","data":{"fileName":"pvscode/alarisAsenaCC"}}')


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8080/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
