# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Nano2
"""
import pkg_resources
import sys
#
import numpy as np

from collections import deque
import serial

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

#
from logging_setup import getLogger
logger = getLogger()

from instruments.data_handler import DataHandler, FinalMeta

class DigitalCounter(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
    def __init__(self, parent=None):
        super().__init__(parent)

        file_layout = 'digital_counter_layout.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename('instruments.digitalcounter', file_layout)
        loadUi(file_layout_path, self)

        self.paired = False
        self.pushButton_updateList.clicked.connect(self._updateListPorts)
        self.pushButton_pair.clicked.connect(self._pairDevice)

    def setDataParams(self, Xdim, Ydim):
        self.dim = (Xdim,Ydim)
        self.imageMap = np.zeros(self.dim)
        self.counterBuffer = deque([],maxlen=100)
        self._setDeviceParams()
        logger.info("Digital Counter got data params")

    def getDataDuringScan(self, indexPos):
        singleValue = self._acquireData()
        self._setPixelData(indexPos, singleValue)

        imageData = self._getIntensityMap()
        curveData = self._getDataBuffer()

        return imageData, curveData

    def getCurveData(self, indexPos):
        return None

    def getRawData(self):
        return self.imageMap

    def getSingleShot(self):
        singleShot = self._acquireData()
        self.lcdNumber_counterValue.display(singleShot)

    def close(self):
        if self.paired == True:
            self.device.close()
            logger.info("Digital Counter Closed")

    ### -------
    def _setPixelData(self, index_pos, value):
        self.imageMap[index_pos[0]][index_pos[1]] = value
        self.counterBuffer.append(value)
        self.lcdNumber_counterValue.display(value)

    def _getIntensityMap(self):
        return self.imageMap

    def _getDataBuffer(self):
        return (range(len(self.counterBuffer)),list(self.counterBuffer))

    def _updateListPorts(self):
        self.listPorts = serial.tools.list_ports.comports()

        self.comboBox_serialPort.clear()
        for port in self.listPorts:
            self.comboBox_serialPort.addItem(port.description)

    def _pairDevice(self):
        if  self.pushButton_pair.isChecked() == True:
            if self.comboBox_serialPort.currentText() != 'None':
                portIndex = self.comboBox_serialPort.currentIndex()
                portDevice = self.listPorts[portIndex].device
                portDescription = self.listPorts[portIndex].description
                boudRate = int(self.lineEdit_boudRate.text())

                try:
                    self.device = serial.Serial(portDevice, boudRate)
                    self.paired = True
                    self.pushButton_pair.setText("Unpair")
                    self.label_deviceStatus.setText("Connected.")
                    logger.info("Device " + portDescription + "connected.")

                except Exception as erro:
                    self.paired = False
                    self.pushButton_pair.setChecked(False)
                    errorMessage =  erro.args[0]
                    self.label_deviceStatus.setText("Erro "+ errorMessage)
                    logger.exception("Error on starting device" + portDescription)
        else:
            if self.paired == True:
                self.device.close()
                logger.info("Digital Counter Closed")
            self.paired = False
            self.pushButton_pair.setText("Pair")
            self.label_deviceStatus.setText("Disconnected.")

    def _setDeviceParams(self):
        stepDelay = float(self.lineEdit_stepDelay.text())*1000
        try:
            self.device.reset_output_buffer()
            self.device.write(str("setparam("+str(int(stepDelay))+","+str(10)+","+str(1000)+","+str(1000)+","+str(0)+")").encode('utf-8'))
            self.label_deviceStatus.setText("Params Set")
            logger.info("Integration time to device: " + str(stepDelay) + ' us')
        except Exception as erro:
            self._clearBuffer()
            error = erro.args[0]
            self.label_deviceStatus.setText("Error. " + error)
            logger.info("Error. " + error)

    def _clearBuffer(self):
        self.device.reset_input_buffer()
        self.device.reset_output_buffer()

    def _acquireData(self):
        self.device.reset_input_buffer()
        raw_data = self.device.readline()
        self.device.flush()
        entryLine = raw_data.decode('utf-8')

        if entryLine[0] == 'A':
            value = float(entryLine[1:])

        return value

    ### --------

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CounterSettings = DigitalCounter()
    CounterSettings.show()
    sys.exit(app.exec_())
