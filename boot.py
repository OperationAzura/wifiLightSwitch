# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

# Complete project details at https://RandomNerdTutorials.com

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'DWW 2.4'
password = 'bazinga1'

station = network.WLAN(network.STA_IF)

#SET STATIC IP
station.ifconfig(('192.168.1.31', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())