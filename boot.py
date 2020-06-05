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

ssid = 'SSID'
password = 'PASSWORD'

station = network.WLAN(network.STA_IF)

#station.ifconfig()
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())