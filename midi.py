#!/usr/bin/env python
import sys
import rtmidi
import threading
import hal, time
h = hal.component('midi')


def print_message(midi, port, hhh):
    if midi.isController():
        print '%s: CONTROLLER' % port, midi.getControllerNumber(), midi.getControllerValue()
        h['m'] = midi.getControllerValue()

class Collector(threading.Thread):
    def __init__(self, device, port, hh):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.hal = hh
        self.quit = False
	print 'Device:', device.getPortName(port)

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
           if self.quit:
                return
           msg = self.device.getMessage()
           if msg:
                print_message(msg, self.portName, self.hal)


dev = rtmidi.RtMidiIn()
collectors = []
h.newpin("m", hal.HAL_S32, hal.HAL_OUT)
h.ready()

for i in range(dev.getPortCount()):
    device = rtmidi.RtMidiIn()
    print 'OPENING',dev.getPortName(i)
    collector = Collector(device, i, h)
    collector.start()
    collectors.append(collector)



print 'HIT ENTER TO EXIT'
sys.stdin.read(1)
for c in collectors:
    c.quit = True
