# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Nano2
"""
import numpy as np
import time

import nidaqmx
from collections import deque

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
import sys

from logging_setup import getLogger
logger = getLogger()

class Counter(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("instruments\counter_layout.ui", self)
        self.conversion = 0.002 #V/counts
        try:
            self.task = nidaqmx.Task()
            self.task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            self.task.start()
            self.label_deviceStatus.setText("Connected.")
            logger.info("Counter Started")
            
        except Exception as erro:
            self.label_deviceStatus.setText("Disconnected."+erro[0])
            logger.exception("Error on starting Piezo")
            
    def setDataParams(self, Xdim, Ydim, nElem):
        self.dim = (Xdim,Ydim)
        self.imageMap = np.zeros(self.dim)
        self.counterBuffer = deque([],maxlen=100)
        logger.info("Counter got data params")
        
    def setScanIndexPath(self, scanIndexPath):
        #scanIndexPath : List of tuples representing the scan current index position
        self.scanIterator = iter(scanIndexPath)
    
    def getDataDuringScan(self):
        time.sleep(float(self.lineEdit_stepDelay.text())/1000) #seconds
        singleValue = self._acquireData()
        curScanPos = next(self.scanIterator)
        self._setPixelData(curScanPos, singleValue)
        
        imageData = self._getIntensityMap()
        curveData = self._getDataBuffer()
        
        return imageData, curveData
    
    def getCurveData(self, pos):
        return None
    
    def close(self):
        self.task.stop()
        self.task.close()
        logger.info("Counter Closed")
    
    ### -------
    def _setPixelData(self, pos, value):
        value = value/self.conversion
        self.imageMap[pos[0]][pos[1]] = value
        self.counterBuffer.append(value)
        self.lcdNumber_counterValue.display(value)
    
    def _getIntensityMap(self):
        return self.imageMap
    
    def _getDataBuffer(self):
        return list(self.counterBuffer)
        
    def _acquireData(self):
        value = self.task.read()
        return value
    
    ### --------
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CounterSettings = Counter()
    CounterSettings.show()
    sys.exit(app.exec_())