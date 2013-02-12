import websocket
import thread
import time
import json
import matplotlib.pyplot as p

reference = 610

command = ""
iterations = 0
yDisplay = []
yOutput = [0]
yVelocity = [0]
T=0.2


def plotResult():
    global iterations, yDisplay, yOutput

    x = range(0,iterations)
    p.plot(x,yDisplay,'r+-', label="Input quantity")
    p.plot([reference for i in x],'b', label = "Reference signal")
    p.step(x,yVelocity,'g', label="Velocity")
    #p.plot(x,yOutput,'g+-')
    p.xlabel("Time")
    p.legend()
    p.show()

def convert(s):
    try:
        return int(s)
    except ValueError:
        return(s)

def parseOutput(output):
    s = output.strip("(##)")
    d = dict(item.split(":=") for item in s.split(",")) # Generate dictionary
    return { k.strip():convert(v.strip()) for k, v in d.iteritems()} # Remove whitespace in dictionary

def sendCommand(command, state):
    state['command'] = command
    cmdstate = '{command}((# display:={display}, step:={step}, timer:={timer} #));'.format(**state);
    d = {"type":"sendCommand", "data":{'command':cmdstate}}
    print "Sending:", d
    ws.send(json.dumps(d))

def on_message(ws, message):
    global command, iterations, yDisplay, yOutput, yVelocity

    print "Message: ", message
    decoded = json.loads(message)
    dtype =  decoded['type']
    
    print 'TYPE:', dtype


    if(dtype == 'processReady'):
        ws.send('{"type":"sendCommand","data":{"command":"press_UP((# display := 0, step := 1, timer := 5 #));"}}')

    if(dtype == 'pvsoutput'):
        iterations += 1
        result = decoded['data']
        output = parseOutput(result[0])
        print 'Output: ', output
        error = reference - output['display']
        yDisplay.append(output['display'])
        print "Error: ", error

        if(iterations > 1):
            yVelocity.append((yDisplay[-1] - yDisplay[-2]) / T)



        if(error > 0):
            if command == "press_DN":
                command = "release_DN"
                yOutput.append(yOutput[-1])
            elif command == "press_dn":
                command = "release_dn"
                yOutput.append(yOutput[-1])
            else:
                command = "press_UP"
                yOutput.append(yOutput[-1]+1)

        if(error < 0):
            if command == "press_UP":
                command = "release_UP"
                yOutput.append(yOutput[-1])
            elif command == "press_up":
                command = "release_up"
                yOutput.append(yOutput[-1])
            else:
                command = "press_DN"
                yOutput.append(yOutput[-1]-1)

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
    ws.send('{"type":"startProcess","data":{"fileName":"pvscode/alarisGS"}}')


if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8080/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
