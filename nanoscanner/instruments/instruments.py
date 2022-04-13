# INSTRUMENTS
from instruments.hyperspectral import hyperspectral
from instruments.counter import counter
from instruments.digitalcounter import digital_counter

def getScanModes():
    scanModes = {
        "Hyperspectral": hyperspectral.Hyperspectral(),
        "Counter": counter.Counter(),
        "DigitalCounter": digital_counter.DigitalCounter()
    }
    return scanModes
