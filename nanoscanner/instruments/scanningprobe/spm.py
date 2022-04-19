# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Allison Pessoa
"""
import sys
import pkg_resources

#
import numpy as np
import time

import nidaqmx
from collections import deque

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

#
from logging_setup import getLogger
logger = getLogger()

from instruments.data_handler import DataHandler, FinalMeta

class Counter(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
    """ Reads the input channel from an Analog-to-Digital Converter. The Conversion
    Factor transforms from voltage to counts (according to the Photon Counter specifications)
    Instruments: * NI-DAQ - BNC2110 - PCI 6014
                 * Home-made photon counter - converts photon pulses in a DC voltage"""

    def __init__(self, parent=None):
        super().__init__(parent)
        file_layout = 'spm_layout.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename('instruments.spm', file_layout)
        loadUi(file_layout_path, self)

        self.lineEdit_stepDelay.editingFinished.connect(self._updateStepDelay)
        self.lineEdit_convFactor.editingFinished.connect(self._updateConvFactor)
        self._updateStepDelay()
        self._updateConvFactor()
        try:
            self.task = nidaqmx.Task()
            self.task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            self.task.start()
            self.label_deviceStatus.setText("Connected.")
            logger.info("Counter Started")

        except Exception as erro:
            self.label_deviceStatus.setText("Disconnected."+erro[0])
            logger.exception("Error on starting Piezo")

    def setDataParams(self, Xdim, Ydim):
        self.dim = (Xdim,Ydim)
        self.imageMap = np.zeros(self.dim)
        self.counterBuffer = deque([],maxlen=100)
        logger.info("Counter got data params")

    def getDataDuringScan(self, indexPos):
        time.sleep(self.stepDelay) #seconds
        singleValue = self._acquireData()
        self._setPixelData(indexPos, singleValue)

        imageData = self._getIntensityMap()
        curveData = self._getDataBuffer()

        return imageData, curveData

    def getCurveData(self, indexPos):
        return None

    def getRawData(self):
        return self.imageMap

    def close(self):
        self.task.stop()
        self.task.close()
        logger.info("Counter Closed")

    ### -------
    def _setPixelData(self, pos, value):
        value = value/self.convFactor
        self.imageMap[pos[0]][pos[1]] = value
        self.counterBuffer.append(value)
        self.lcdNumber_counterValue.display(value)

    def _updateStepDelay(self):
        self.stepDelay = float(self.lineEdit_stepDelay.text())/1000

    def _updateConvFactor(self):
        self.convFactor = float(self.lineEdit_convFactor.text())

    def _getIntensityMap(self):
        return self.imageMap

    def _getDataBuffer(self):
        return (range(len(self.counterBuffer)),list(self.counterBuffer))

    def _acquireData(self):
        value = self.task.read()
        return value

    ### --------

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CounterSettings = Counter()
    CounterSettings.show()
    sys.exit(app.exec_())
