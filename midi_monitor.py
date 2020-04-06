#!/usr/bin/python
# From https://github.com/patrickkidd/pyrtmidi
import sys
import rtmidi
import threading

def print_message(midi, port):
    if midi.isNoteOn():
        print '%s: ON: ' % port, midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity()
    elif midi.isNoteOff():
        print '%s: OFF:' % port, midi.getMidiNoteName(midi.getNoteNumber())
    elif midi.isController():
        print '%s: CONTROLLER' % port, midi.getControllerNumber(), midi.getControllerValue()

class Collector(threading.Thread):
    def __init__(self, device, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            msg = self.device.getMessage()
            if msg:
                print_message(msg, self.portName)


dev = rtmidi.RtMidiIn()
collectors = []
for i in range(dev.getPortCount()):
    device = rtmidi.RtMidiIn()
    print 'OPENING',dev.getPortName(i)
    collector = Collector(device, i)
    collector.start()
    collectors.append(collector)


print 'HIT ENTER TO EXIT'
sys.stdin.read(1)
for c in collectors:
    c.quit = True
