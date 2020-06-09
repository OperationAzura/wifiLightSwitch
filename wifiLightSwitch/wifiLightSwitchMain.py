from machine import Pin
import socket

import _thread
import time
import utime
import machine
import wifiLightSwitch.uftpd

def resetSwitch():
    machine.reset()

def startResetTimer():
    timer = machine.Timer(0)  
    timer.init(period=60000, mode=machine.Timer.PERIODIC, callback=resetSwitch)
 
def logToFile(s):
    f = open('log.log', 'w')
    st = str(time.time())
    f.write((st + s))
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
        #self.pysicalSwitchState = self.switchPin.value()
        self.switchPin.irq(trigger=Pin.IRQ_FALLING, handler=self.pysicalSwitchToggle)
        self.pysicalSwitchTimer = utime.ticks_ms()
        
        print('Switch created!')
        print('Name: ', name)
        #print('ticks_ms: ', self.pysicalSwitchTimer)

    def toggle(self):
        if self.relayPin.value() == 1:
            self.relayPin.value(0)
            logToFile('Toggle off' + self.name)
        else:
            self.relayPin.value(1)
            logToFile('Toggle on' + self.name)
    
def watchPysicalSwitch(s):
    while True:
        print(s)
        print('current state: ', s.pysicalSwitchState)
        state = s.switchPin.value()
        print('new state: ', state)
        if state != s.pysicalSwitchState:
            s.pysicalSwitchState = state
            print('pysical state set to: ', state)
            s.toggle()
        time.sleep(0.5)
                
def watchPysicalSwitches(switches):
    while True:
        for s in switches:
            pass
            
                
        time.sleep(0.5)

def web_page():
  htmlFile = open("wifiLightSwitch/index.html", "r")
  html = htmlFile.read()
  htmlFile.close()
  #html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  #<link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  #h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  #border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  #.button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  #<p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  #<p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html

def run():
    logToFile('RUN starting')
    startResetTimer()
    switches = []
    switch = Switch('Storage Room', 12, 13)
    switches.append(switch)
    #_thread.start_new_thread(watchPysicalSwitch, ( switches))
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        #print(switchSignalIn.value())
        conn, addr = s.accept()
        try:
            #response = ''
            request = conn.recv(1024)
            request = str(request)
            
            line1On = request.find('/?line1=on')
            line1Off = request.find('/?line1=off')
            servLog = request.find('/log')
            reset = request.find('/resetSwitch')
            #line2On = request.find('/?line2=on')
            #line2Off = request.find('/?line2=off')
            if line1On == 6:
                switch.toggle()
                response = 'line 1 on'
                logToFile('line 1 on recieved')
            elif line1Off == 6:
                switch.toggle()
                response = 'line 1 off'
                logToFile('line 1 off recieved')
            elif servLog == 6:
                logToFile('log request recieved')
                f = open('log.log')
                response = f.read()
                f.close()
            elif reset == 6:
                logToFile('reset request recieved')
                response = 'resetting'
                resetSwitch()
            #elif line2On == 6:
            #    line2.value(1)
            #    response = 'line 2 on'
            #elif line2Off == 6:
            #    line2.value(0)
            #    response = 'line 2 off'
            else:
                response = web_page()
            
            #response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Access-Control-Allow-Origin: *')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        except Exception as e:
            print('EXCEPTION!!!')
            logException(e)
            
            
    conn.close()
