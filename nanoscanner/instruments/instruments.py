# INSTRUMENTS
from instruments.hyperspectral import hyperspectral
from instruments.analogcounter import analog_counter
from instruments.digitalcounter import digital_counter
from instruments.arduinocounter import arduino_counter

def getScanModes():
    scanModes = {
        "DigitalCounter": digital_counter.Counter(),
        #"AnalogCounter": analog_counter.Counter(),
        "Hyperspectral": hyperspectral.Hyperspectral(),
        "ArduinoCounter": arduino_counter.DigitalCounter(),
    }
    return scanModes
