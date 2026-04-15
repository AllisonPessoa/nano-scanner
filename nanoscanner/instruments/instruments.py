# INSTRUMENTS
from instruments.hyperspectral import hyperspectral
from instruments.analogcounter import analog_counter
from instruments.digitalcounter import digital_counter
from instruments.arduinocounter import arduino_counter
from instruments.TCSPC import TCSPC

def getScanModes():
    scanModes = {
        "DigitalCounter": digital_counter.Counter(),
        #"AnalogCounter": analog_counter.Counter(),
        "Hyperspectral": hyperspectral.Hyperspectral(),
        "ArduinoCounter": arduino_counter.DigitalCounter(),
        "TCSPC": TCSPC.TCSPC(),
    }
    return scanModes
