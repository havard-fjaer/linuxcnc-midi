#!/usr/bin/env python
# Install with: sudo halcompile --install --userspace midi.py
import sys
import rtmidi
import threading
import hal
import time
halMidi = hal.component('midi')
debug = False
class Collector(threading.Thread):
    def __init__(self, device, port, hal):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.midiDevice = device
        self.hal = hal
        self.quit = False

    def run(self):
        self.midiDevice.openPort(self.port)
        self.midiDevice.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            # Read any available MIDI message
            midiMessage = self.midiDevice.getMessage()
            if midiMessage and midiMessage.isController():
                controllerNumber = midiMessage.getControllerNumber()
                controllerValue = midiMessage.getControllerValue()
                if debug:
                    print(controllerNumber, controllerValue)
                # Map MIDI message to HAL pin
                self.hal[str(self.port) + '.controller.' + str(controllerNumber) + '.out'] = controllerValue


try:
    midiIn = rtmidi.RtMidiIn()
    collectors = []
    
    # Go through all MIDi devices
    for port in range(midiIn.getPortCount()):
        midiDevice = rtmidi.RtMidiIn()
        if debug:
            print(midiIn.getPortName(port))

        collector = Collector(midiDevice, port, halMidi)
        collector.start()
        collectors.append(collector)

        # Add HAL pins for all possible MIDI controllers on each device
        # (I don't see how I would identify what controllers that actually are present on a device)
        for controller in range(0, 127):
            halPinName = str(port) + ".controller." + str(controller) + '.out'
            if debug:
                print(halPinName)
            halMidi.newpin(halPinName, hal.HAL_S32, hal.HAL_OUT)
    halMidi.ready()

    # Wait
    while True:
        time.sleep(1)

# Clean up
finally:
    for c in collectors:
        c.quit = True
    # If HAL is not closed, the component might stand in the way when trying to spin up the script again
    halMidi.exit()
