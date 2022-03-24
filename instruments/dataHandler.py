# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 16:40:33 2021

@author: Nano2
"""
from abc import ABC, abstractmethod
from PyQt5 import QtWidgets
        
class DataHandler(ABC):
    
    @abstractmethod
    def setDataParams(self, Xdim, Ydim):
        """Creates the data set for a scan, Xdim and Ydim represent the scan matrix dimensions. For example, hyperspectral scanning uses a (Xdim, Ydim, 1024) numpy array. Each pixel represents a spectrum"""
        pass
    
    @abstractmethod
    def getDataDuringScan(self, indexPos):
        """ Returns the data to be shown during the scan.  It is possible to return an image data and a plot data in this order. Plot data can be omitted. 
        Image data structure is a multidimensional (Xdim, Ydim) numpy array with floats eg. np.ones((Xdim,Ydim)). 
        Plot data sctructure is a (X_data, Y_data) floats """
        pass
    
    @abstractmethod
    def getCurveData(self, indexPos):
        """ If there is a plot data for each pixel (indexPos representing the index position), return the plot data numpy array with this method. If it is now the case, retur None """
        pass
    
    @abstractmethod
    def getRawData(self):
        """ Returns the numpy data structure to be saved """
        pass
    
    @abstractmethod
    def close(self):
        """ Close the communication with the instruments securetely """
        pass

class FinalMeta(type(QtWidgets.QWidget), type(DataHandler)):
    pass
