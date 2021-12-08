# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Nano2
"""
import numpy as np
from astropy.io import fits
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

import pyqtgraph as pg

import os
import sys
import time

class Hyperspectral(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("instruments\hyper_layout.ui", self)
        self.fileName = r'C:\Users\Nano2\Desktop\Allison\Microscopia Hiperespectral\files\espectro.fits'
        self.flagName = r'C:\Users\Nano2\Desktop\Allison\Microscopia Hiperespectral\files\flag.fits'
    
    def setDataParams(self, Xdim, Ydim, nElem):
        self.dim = (Xdim,Ydim)
        dt = np.dtype((np.float32, nElem))
        self.hyperData = np.zeros(self.dim, dtype = dt)
        
    def setScanIndexPath(self, scanIndexPath):
        #scanIndexPath : List of tuples representing the scan current index position
        self.scanIterator = iter(scanIndexPath)
    
    def getDataDuringScan(self):
        curScanIndexPos = next(self.scanIterator)
        self._setPixelData(curScanIndexPos, self._acquireData())
        
        imageData = self._getIntensityMap()
        curveData = self.getCurveData(curScanIndexPos)
        self.lcdNumber_hyperValue.display(self._getPixelValue(curScanIndexPos))
        
        return imageData, curveData
    
    def getCurveData(self, indexPos):
        return self.hyperData[indexPos[0], indexPos[1]]
    
    def close(self):
        print("Hyperspectral Closed")
    
    ### --------
    
    def _setPixelData(self, indexPos, data):
        self.hyperData[indexPos[0], indexPos[1]] = data
    
    def _getPixelValue(self, indexPos):
        wavelength = int(self.lineEdit_singleBandRange.text())
        return self.hyperData[indexPos[0]][indexPos[1]][wavelength]
        
    def _getIntensityMap(self):
        self.intensityMap = np.zeros(self.dim)
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.intensityMap[x][y] = self._getPixelValue((x,y))
        
        return self.intensityMap
    
    def _acquireData(self):
        spectrum = None
        timeout = time.time() + 5
        
        originalTime = os.path.getmtime(self.flagName)
        while(time.time() < timeout):
            try:
                curModTime = os.path.getmtime(self.flagName)
                assert type(curModTime) == float #When it gets a float
                
                if (curModTime > originalTime):
                    try:
                        file = fits.open(self.fileName)
                        spectrum = file[0].data
                        file.close()
                        break
                    except:
                        print("Erro on reading original file")
                        
            except:
                pass
        
        return spectrum
    
    
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    HyperSettings = Hyperspectral()
    HyperSettings._acquireData()
    HyperSettings.show()
    sys.exit(app.exec_())