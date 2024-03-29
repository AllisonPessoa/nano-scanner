# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Nano2
"""
import pkg_resources

import os, sys, inspect
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

#
import numpy as np

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

import time

#
from logging_setup import getLogger
logger = getLogger()

from instruments.data_handler import DataHandler, FinalMeta

class Hyperspectral(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
    def __init__(self, parent=None):
        super().__init__(parent)

        file_layout = 'hyper_layout.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename('instruments.hyperspectral', file_layout)
        loadUi(file_layout_path, self)

        self.toolButton_selectFolder.clicked.connect(self._selectFolder)
        logger.info("Hyperspectral Started")

    def setDataParams(self, Xdim, Ydim):
        if self.lineEdit_fileFolder.text() == '':
            logger.info("Folder to spectrum files not specified")
            self._selectFolder()

        self.fileName = self.lineEdit_fileFolder.text() + '/espectro.asc'

        self.dim = (Xdim,Ydim)
        dt = np.dtype((np.float32, 1024))
        self.hyperData = np.zeros(self.dim, dtype = dt)
        logger.info("Hyperspectral got data params")

    def getDataDuringScan(self, indexPos):
        self._setPixelData(indexPos, self._acquireData())

        imageData = self._getIntensityMap()
        curveData = self.getCurveData(indexPos)
        self.lcdNumber_hyperValue.display(self._getPixelValue(indexPos))

        return imageData, curveData

    def getCurveData(self, indexPos):
        return (self.wavelength, self.hyperData[indexPos[0], indexPos[1]])

    def getRawData(self):
        return (self.wavelength, self.hyperData)

    def close(self):
        logger.info("Hyperspectral closed")

    ### --------
    def _selectFolder(self):
        fileName = QtWidgets.QFileDialog.getExistingDirectory(
        caption = "Select File Folder")

        if fileName:
            self.lineEdit_fileFolder.setText(fileName)

        logger.info("New Folder to spectrum files specified")

    def _setPixelData(self, indexPos, data):
        if indexPos[0] == 0 and indexPos[1] == 0:
            self.wavelength, intensity = data
        intensity = data[1]
        self.hyperData[indexPos[0], indexPos[1]] = np.array(intensity)

    def _getPixelValue(self, indexPos):
        index = int(self.lineEdit_falseColorIndex.text())
        return (self.hyperData[indexPos[0], indexPos[1]][index])

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
    #HyperSettings._acquireData()
    HyperSettings.show()
    sys.exit(app.exec_())
