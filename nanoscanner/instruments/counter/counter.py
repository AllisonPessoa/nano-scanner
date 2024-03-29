# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Allison
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
        file_layout = 'counter_layout.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename('instruments.counter', file_layout)
        loadUi(file_layout_path, self)

        self.counterBuffer = deque([],maxlen=100)

        self.lineEdit_samplingNumber.editingFinished.connect(self._updateSamplingNumber)
        self.lineEdit_convFactor.editingFinished.connect(self._updateConvFactor)
        self.comboBox_analogChannel.currentIndexChanged.connect(self._changeAnalogInput)
        self._updateSamplingNumber()
        self._updateConvFactor()
        self._startAnalogInput()

    def setDataParams(self, Xdim, Ydim):
        self.dim = (Xdim,Ydim)
        self.imageMap = np.zeros(self.dim)
        logger.info("Counter got data params")

    def getDataDuringScan(self, indexPos):
        mean = self._integrateCounts() #time delay in seconds
        self._setPixelData(indexPos, mean)

        imageData = self._getIntensityMap()
        curveData = self._getDataBuffer()

        return imageData, curveData

    def getCurveData(self, indexPos):
        return None

    def getRawData(self):
        return self.imageMap

    def close(self):
        try:
            self.task.stop()
            self.task.close()
            logger.info("Counter Closed")
        except Exception as erro:
            self.label_deviceStatus.setText("Device not propery closed. " + erro)
            logger.exception("Error on closing Piezo")

    def getSingleShot(self):
        pass

    ### -------
    def _integrateCounts(self):
        cumulative = 0
        for i in range(self.samplingNumber):#while time.time() < (current_time + interval):
            cumulative += self._acquireData()*self.convFactor

        mean = cumulative/self.samplingNumber
        return mean

    def _startAnalogInput(self):
        try:
            self.task = nidaqmx.Task()
            channel = self.comboBox_analogChannel.currentText()
            self.task.ai_channels.add_ai_voltage_chan(channel)
            self.task.start()
            self.label_deviceStatus.setText("Connected. Channel " + channel)
            logger.info("Counter Started - channel " + channel)

        except Exception as erro:
            self.label_deviceStatus.setText("Disconnected. - Erro. See Log File")
            logger.exception("Error on starting Piezo")

    def _changeAnalogInput(self):
        self.close()
        self._startAnalogInput()

    def _setPixelData(self, pos, value):
        self.imageMap[pos[0]][pos[1]] = value
        self.counterBuffer.append(value)
        self.lcdNumber_counterValue.display(value)

    def _updateSamplingNumber(self):
        self.samplingNumber = int(float(self.lineEdit_samplingNumber.text()))

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
