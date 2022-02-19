from machine import Pin
import socket

import _thread
import time
import utime
import machine
#import wifiLightSwitch.uftpd

### quick fix for crash
f = open('log.log', 'w')
f.write('')
f.close()

def resetSwitch(a):
    logToFile('restarting')
    machine.reset()

def startResetTimer():
    timer = machine.Timer(0)
    #86400 seconds in a day
    timer.init(period=86400000, mode=machine.Timer.PERIODIC, callback=resetSwitch)
 
def logToFile(s):
    old = ''
    try:
        f = open('log.log', 'r')
        old = f.read()
        f.close()
    except Exception as e:
        print('EXCEPTION: log most likely not created yet, attempting to create')
        print(e)
    f = open('log.log', 'w')
    f.write(old)
    f.write('\n')
    f.write(s)
    f.close()

def getLog():
    l = ''
    try:
        f = open('log.log')
        l = f.read()
        f.close()
    except Exception as e:
        print('Exception getting log: ', e)
        f.close()
        l = 'no log exists'
    if l == '':
        l = 'no log exists'
    return l
        
        

def clearLog():
    f = open('log.log', 'w')
    f.write('')
    f.close()
        
def logException(e):
    import sys
    logToFile(str(sys.print_exception(e)))
    sys.print_exception(e)
    

class Switch:
    def __init__(self, name, relayPinNumber, switchPinNumber, defaultShutOffTimer=15):
        self.name = name
        self.relayPin = Pin(relayPinNumber, Pin.OUT)
        self.switchPin = Pin(switchPinNumber, Pin.IN, Pin.PULL_DOWN)
        self.pysicalSwitchState = self.switchPin.value()
        self.shutOffTimer = machine.Timer(1)  
        self.shutOffTime = defaultShutOffTimer * 60000 #60000 = minute
        #self.adc = machine.ADC(self.switchPin)
        print('Switch created!')
        print('Name: ', name)

    def toggle(self):
        if self.relayPin.value() == 0:
            self.relayPin.value(1)
            self.stopTimer()
            return self.name + " OFF: " + str(self.relayPin.value())
        else:
            self.relayPin.value(0)
            self.stopTimer()
            self.startTimer()
            return self.name + " ON: " + str(self.relayPin.value())
    #getState gets the on / off state of the light
    def getState(self):
        state = 'ON: ' + str(self.relayPin.value())
        if self.relayPin.value() == 1:
            state = 'OFF: ' + str(self.relayPin.value())
        return state

    #analogGraph reads the ADC value, calculates it to a 3.3v scale and makes a crude bar graph
    def analogGraph(self):
        v = int((self.adc.read() / 4095) * 50)
        x = 0
        bar = str((v / 50) * 3.3) + ' '
        while x <= v:
            x = x + 1
            bar = bar + 'X'
        return bar
    #getTimer get the current state of the shut off timer
    def getTimer(self):
        return self.shutOffTimer

    #startTimer starts the shutOffTimer
    def startTimer(self):
        self.shutOffTimer.init(period=self.shutOffTime, mode=machine.Timer.ONE_SHOT, callback=self.turnLightOff)
    
    #stopTimer shuts the shut off timer off
    def stopTimer(self):
        self.shutOffTimer.deinit()


    #setTimer sets the shut off timer
    def setTimer(self, timer):
        #60000 = minute
        self.shutOffTime = (60000 * timer)
        self.stopTimer()
        self.startTimer()
        return str(self.shutOffTime)
    
    #turnLightOff is used with a timer to make sure the light shuts off
    def turnLightOff(self, a):
        print('shut off timer fired')
        if self.relayPin.value() == 0:
            print('shutting light off')
            self.toggle()
        else:
            print('the light was off already')
             
def watchPysicalSwitch(s):
    while True:
        state = s.switchPin.value() 
        if state != s.pysicalSwitchState:
            s.pysicalSwitchState = state
            logToFile('pysical state set to: ' + str(state))
            s.toggle()
        time.sleep(0.4)
                
def watchPysicalSwitches(switches):
    logToFile('watching sweitches:')
    for s in switches:
        logToFile(s.name())
    while True:
        for s in switches:
            state = s.switchPin.value()
            if state != s.pysicalSwitchState:
                s.pysicalSwitchState = state
                logToFile('pysical state set to: ', state)
                s.toggle()
            time.sleep(0.5)
            
                
        time.sleep(0.5)

def web_page():
    htmlFile = open("wifiLightSwitch/index.html", "r")
    html = htmlFile.read()
    htmlFile.close()
    return html

def sendHTTP(conn, response):
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Access-Control-Allow-Origin: *')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()

def run():
    
    logToFile('RUN starting')
    startResetTimer()
    switches = []
    switch = Switch('Storage Room', 13, 36)
    switches.append(switch)
    _thread.start_new_thread(watchPysicalSwitch, ( switches))
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        try:
            response = ''
            request = str(conn.recv(1024))
            
            line1On = request.find('/?line1=on')
            servLog = request.find('/log')
            reset = request.find('/resetSwitch')
            getStateHandler = request.find('/getState')
            getTimerHandler = request.find('/getTimer')
            setTimerHandler = request.find('/setTimer')
            clearLogHandler = request.find('/clearLog')
            if line1On == 6:
                response = switch.toggle()
                logToFile('line 1 toggle recieved')
                sendHTTP(conn, response)
            elif servLog == 6:
                response = getLog()
                sendHTTP(conn, response)
            elif getStateHandler == 6:
                response = switch.getState()
                sendHTTP(conn, response)
            elif reset == 6:
                logToFile('reset request recieved')
                response = 'resetting'
                sendHTTP(conn, response)
                resetSwitch(1)
            elif getTimerHandler == 6:
                logToFile('getting timer: ')
                response = switch.getTimer()
                logToFile(response)
                sendHTTP(conn, response)
            elif setTimerHandler == 6:
                logToFile('setting timer: ')
                response = switch.setTimer(int(request[setTimerHandler+9:request.find(' HTTP')]))
                logToFile(response)
                sendHTTP(conn, response)
            elif clearLogHandler == 6:
                clearLog()
                sendHTTP(conn, 'log cleared')
            else:
                response = web_page()
                sendHTTP(conn, response)
            
        except Exception as e:
            logException(e)
            conn.close()
            
               
        
