from machine import Pin
import socket

import _thread
import time
import utime
import machine
#import wifiLightSwitch.uftpd

def resetSwitch(a):
    logToFile('restarting')
    machine.reset()

def startResetTimer():
    timer = machine.Timer(0)  
    timer.init(period=60000, mode=machine.Timer.PERIODIC, callback=resetSwitch)
 
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

def logException(e):
    import sys
    logToFile(sys.print_exception(e))
    sys.print_exception(e)
    

class Switch:    
    def pysicalSwitchToggle(self, pin):
        if abs(time.ticks_ms() - self.pysicalSwitchTimer) > 500:
            self.toggle()
            self.pysicalSwitchTimer = utime.ticks_ms()
        else:
            logToFile('IRQ triggered too soon!!! ')
        
    def __init__(self, name, relayPinNumber, switchPinNumber):
        self.name = name
        self.relayPin = Pin(relayPinNumber, Pin.OUT)
        self.switchPin = Pin(switchPinNumber, Pin.IN, Pin.PULL_DOWN)
        self.pysicalSwitchState = self.switchPin.value()
        #self.switchPin.irq(trigger=Pin.IRQ_FALLING, handler=self.pysicalSwitchToggle)
        self.pysicalSwitchTimer = utime.ticks_ms()
        #self.adc = machine.ADC(self.switchPin)
        print('Switch created!')
        print('Name: ', name)
        #print('ticks_ms: ', self.pysicalSwitchTimer)

    def toggle(self):
        if self.relayPin.value() == 1:
            self.relayPin.value(0)
            return self.name + "ON"
        else:
            self.relayPin.value(1)
            return self.name + "OFF"
     
    #analogGraph reads the ADC value, calculates it to a 3.3v scale and makes a crude bar graph
    def analogGraph(self):
        v = int((self.adc.read() / 4095) * 50)
        x = 0
        bar = str((v / 50) * 3.3) + ' '
        while x <= v:
            x = x + 1
            bar = bar + 'X'
        return bar
        
            
    
def watchPysicalSwitch(s):
    while True:
        state = s.switchPin.value() 
        if state != s.pysicalSwitchState:
            s.pysicalSwitchState = state
            logToFile('pysical state set to: ' + str(state))
            s.toggle()
        time.sleep(0.5)
                
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
            request = conn.recv(1024)
            request = str(request)
            
            line1On = request.find('/?line1=on')
            servLog = request.find('/log')
            reset = request.find('/resetSwitch')
            if line1On == 6:
                response = switch.toggle()
                logToFile('line 1 toggle recieved')
                sendHTTP(conn, response)
            elif servLog == 6:
                logToFile('log request recieved')
                f = open('log.log')
                response = f.read()
                f.close()
                sendHTTP(conn, response)
            elif reset == 6:
                logToFile('reset request recieved')
                response = 'resetting'
                sendHTTP(conn, response)
                resetSwitch()
            else:
                response = web_page()
                sendHTTP(conn, response)
            
        except Exception as e:
            logException(e)
            conn.close()
            
               
        
