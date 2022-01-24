# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 16:40:33 2021

@author: Nano2
"""
from abc import ABC, abstractmethod
        
class DataHandler(ABC):
    
    @abstractmethod
    def setDataParams(self, Xdim, Ydim):
        pass
    
    @abstractmethod
    def setScanIndexPath(self, scanIndexPath):
        pass
    
    @abstractmethod
    def getDataDuringScan(self):
        pass
    
    @abstractmethod
    def getCurveData(self, indexPos):
        pass
    
    @abstractmethod
    def getRawData(self):
        pass
    
    @abstractmethod
    def close(self):
        pass
    