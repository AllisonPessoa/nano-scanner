# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Nano2
"""
import numpy as np
from scipy import integrate

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

import os
import sys
import time

from logging_setup import getLogger
logger = getLogger()

from dataHandler import DataHandler

class FinalMeta(type(QtWidgets.QWidget), type(DataHandler)):
    pass

class Hyperspectral(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("instruments\hyper_layout.ui", self)
        self.fileName = r'C:\Users\Nano2\Desktop\Allison\Microscopia Hiperespectral\files\espectro.asc'
        logger.info("Hyperspectral Started")
        
    def setDataParams(self, Xdim, Ydim, nElem):
        self.dim = (Xdim,Ydim)
        dt = np.dtype((np.float32, nElem))
        self.hyperData = np.zeros(self.dim, dtype = dt)
        logger.info("Hyperspectral got data params")
        
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
        return (self.wavelength, self.hyperData[indexPos[0], indexPos[1]])
    
    def getRawData(self):
        return (self.wavelength, self.hyperData)
    
    def close(self):
        logger.info("Hyperspectral closed")
    
    ### --------
    
    def _setPixelData(self, indexPos, data):
        if indexPos[0] == 0 and indexPos[1] == 0:
            self.wavelength, intensity = data
            self._setWavelengthsIndexes()
        intensity = data[1]
        self.hyperData[indexPos[0], indexPos[1]] = np.array(intensity)
    
    def _setWavelengthsIndexes(self):
        wavelength_0 = int(self.lineEdit_singleBand0.text())
        wavelength_1 = int(self.lineEdit_singleBand1.text())
        
        self.single_index_0 = self._getIndex(self.wavelength, wavelength_0)
        self.single_index_1 = self._getIndex(self.wavelength, wavelength_1)
        
        sup_0 = int(self.lineEdit_bandRatioSup0.text())
        sup_1 = int(self.lineEdit_bandRatioSup1.text())
        inf_0 = int(self.lineEdit_bandRatioInf0.text())
        inf_1 = int(self.lineEdit_bandRatioInf1.text())
        
        self.dual_ind_sup_0 = self._getIndex(self.wavelength, sup_0)
        self.dual_ind_sup_1 = self._getIndex(self.wavelength, sup_1)
        self.dual_ind_inf_0 = self._getIndex(self.wavelength, inf_0)
        self.dual_ind_inf_1 = self._getIndex(self.wavelength, inf_1)
            
    def _getPixelValue(self, indexPos):
        
        if self.radioButton_hyper_singleBand.isChecked():
            band_int = self._getBandIntensity(self.hyperData[indexPos[0]][indexPos[1]],
                                              self.single_index_0,
                                              self.single_index_1)
            
            return band_int
        
        else: #Band Ratio
            sup_band_int = self._getBandIntensity(self.hyperData[indexPos[0]][indexPos[1]],
                                                  self.dual_ind_sup_0,
                                                  self.dual_ind_sup_1)
            inf_band_int = self._getBandIntensity(self.hyperData[indexPos[0]][indexPos[1]],
                                                  self.dual_ind_inf_0,
                                                  self.dual_ind_inf_1)
            LIR = float(sup_band_int/inf_band_int)
            
            if np.isnan(LIR) is not 1 and LIR < 1:
                return LIR
            else:
                return 0
    
    def _getBandIntensity(self, data, index_0, index_1):
        
        wave_to_integrate =  self.wavelength[index_0 : index_1]
        counts_to_integrate =  data[index_0 : index_1]
        
        band_integral = integrate.simpson(counts_to_integrate, wave_to_integrate)
        
        return band_integral
        
    def _getIndex(self, data, value):
        diff = lambda list_value : abs(list_value - value)
        closest_value = min(data, key=diff)
        index = data.index(closest_value)
        return index
        
    def _getIntensityMap(self):
        self.intensityMap = np.zeros(self.dim)
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.intensityMap[x][y] = self._getPixelValue((x,y))
        
        return self.intensityMap
    
    def _acquireData(self):
        wavelength, intensity = [], []
        timeout = time.time() + 5

        while(time.time() < timeout):
            try:
                os.rename(self.fileName, self.fileName)
                break
            except:
                pass
        try:
            file = open(self.fileName, 'r')
            for line in file.readlines():
                wavelength.append(float(line.split(',')[0]))
                intensity.append(float(line.split(',')[1]))
        except Exception as error:
            print('Erro'+ str(error))
        
        file.close()
        os.remove(self.fileName)
        
        return wavelength, intensity
    
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    HyperSettings = Hyperspectral()
    HyperSettings._acquireData()
    HyperSettings.show()
    sys.exit(app.exec_())