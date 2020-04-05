#!/usr/bin/env python
#Install with: sudo halcompile --install --userspace midi.py 
import sys
import rtmidi
import threading
import hal, time
halMidi = hal.component('midi')

debug = False


class Collector(threading.Thread):
    def __init__(self, device, port, hal):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.hal = hal
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
           if self.quit:
                return
           midiMessage = self.device.getMessage()
           if midiMessage and midiMessage.isController():
                controllerNumber = midiMessage.getControllerNumber()
                controllerValue = midiMessage.getControllerValue()
                if debug:
                    print(controllerNumber, controllerValue)
                self.hal[str(self.port) + '.controller.'+ str(controllerNumber) + '.out']  = controllerValue 

try:
    midiIn = rtmidi.RtMidiIn()
    collectors = []

    
    for port in range(midiIn.getPortCount()):
        midiDevice = rtmidi.RtMidiIn()    
        midiPortName = midiIn.getPortName(port)
        if debug:
            print(midiPortName)
        collector = Collector(midiDevice, port, halMidi)
        
        collector.start()
        collectors.append(collector)

        for controller in range(0, 127):
            halPinName = str(port) + ".controller." + str(controller) + '.out'
            if debug:
                print(halPinName)
            halMidi.newpin(halPinName, hal.HAL_S32, hal.HAL_OUT)
    halMidi.ready()
    while True: 
        time.sleep(1)

    for c in collectors:
        c.quit = True
finally:
    halMidi.exit()