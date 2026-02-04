# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import network
def checkwlan():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('NETWORK NAME', 'password')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

checkwlan()

import webrepl
webrepl.start()
