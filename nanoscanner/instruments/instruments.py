# INSTRUMENTS
from instruments.hyperspectral import hyperspectral
from instruments.counter import counter
from instruments.digitalcounter import digital_counter

def getScanModes():
    scanModes = {
        "Counter": counter.Counter(),
        "Hyperspectral": hyperspectral.Hyperspectral(),
        "DigitalCounter": digital_counter.DigitalCounter()
    }
    return scanModes
