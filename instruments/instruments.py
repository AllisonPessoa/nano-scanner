# INSTRUMENTS
import hyperspectral
import counter
import digitalCounter

def getScanModes():
    scanModes = {
        "Hyperspectral": hyperspectral.Hyperspectral(),
        "Counter": counter.Counter(),
        "DigitalCounter": digitalCounter.DigitalCounter()
    }
    return scanModes
