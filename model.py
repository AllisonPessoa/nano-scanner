#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 14:23:49 2021

@author: allison
"""
import time
import sys
import os.path
sys.path.append(os.path.abspath("instruments"))

# INSTRUMENTS
import piezoSystem
import hyperspectral
import counter

from PyQt5 import QtWidgets, QtCore
import pickle

class Model(QtCore.QObject):

    def __init__(self, piezoParams, scanParams):
        super(Model, self).__init__()
        ### POSITIONING ###
        self.posRel={"X": 0, "Y": 0,
                     "Xindex": 0, 'Yindex': 0}
        
        self.posAbs={"X": 0, "Y": 0}
        self.relMoveLocker = True    
        
        self.setScanParams(scanParams)
        self.dataHandler = None
        self.scanAbort = False
        
        ### INSTRUMENTS INIT ###
        self.piezo = piezoSystem.PiezoCommunication(piezoParams)

    # Signals to update View
    emitFinished = QtCore.pyqtSignal()
    emitCurveData = QtCore.pyqtSignal(object)
    emitImageData = QtCore.pyqtSignal(object)
    emitRelPos = QtCore.pyqtSignal(dict)
    emitCenterPos = QtCore.pyqtSignal(dict)
    emitError = QtCore.pyqtSignal(str)
    emitVoltageStatus = QtCore.pyqtSignal(float, float)
    emitProgress = QtCore.pyqtSignal(float)
    
    def getScanModes(self):
        self.scanModes = {
            "Hyperspectral": hyperspectral.Hyperspectral(),
            "Counter": counter.Counter()}
        return self.scanModes
        
    def _roundToAxis(self, value, stepSize):
        if (value % stepSize) <= int(stepSize/2):
            value = int(round(value - (value % stepSize),0))
            return value
        else:
            value = int(round(value + stepSize - \
                              (value % stepSize),0))
            return value
    
    def setScanParams(self, parameters):
        self.scanRange = {'X': parameters["Xrange"],
                          'Y': parameters["Yrange"]}
        
        self.scanNumSteps = {'X': parameters["nXsteps"],
                             'Y': parameters["nYsteps"]}
        
        self.scanStepSize = {'X': parameters["XstepSize"],
                             'Y': parameters["YstepSize"]}
        
        self.scanCenter = {'X': parameters["Xcenter"],
                           'Y': parameters["Ycenter"]}
        
    def startScan(self, mode):     
        scanPath, indexScanPath = self._calculateSteps() ##Calculate previously the scan path
        totalScanLen = self.scanNumSteps['X']*self.scanNumSteps['Y']
        
        modeKey = next(x for x in self.scanModes.keys() if x == mode)
        self.dataHandler = self.scanModes[modeKey]
        self.dataHandler.setDataParams(self.scanNumSteps['X'], \
                                       self.scanNumSteps['Y'], 1024)
        
        self.dataHandler.setScanIndexPath(indexScanPath)
        
        for index, pos in enumerate(scanPath):
            if self.scanAbort == False:
                try:
                    imageData, curveData = self.dataHandler.getDataDuringScan()
                    self.emitImageData.emit(imageData)
                    self.emitCurveData.emit(curveData)
                    
                except Exception as erro:
                    errorMessage = erro.args[0]
                    self.emitError.emit('Error on acquiring data: '+str(errorMessage))
                    break
                
                #Update scan position
                self.drivePiezo(pos)
                self.emitProgress.emit((index/totalScanLen)*100)
            else:
                break
        self.finishScan()
    
    def endApplication(self):
        self.drivePiezo({'X': 0, 'Y': 0})
        self.piezo.close()
        for instrum in self.scanModes.keys():
            self.scanModes[instrum].close()
        
    def finishScan(self):
        self.emitFinished.emit()
    
    def _calculateSteps(self):
        path = [{'X': self.scanCenter['X'] -  self.scanRange['X']/2,
                 'Y': self.scanCenter['X'] -  self.scanRange['Y']/2}]
        indexPath = [(0,0)]
        
        nXsteps = self.scanNumSteps['X']
        nYsteps = self.scanNumSteps['Y']
        XstepSize = self.scanStepSize['X']
        YstepSize = self.scanStepSize['Y']
        
        for i in range(nYsteps):
            if i % 2 == 0:
                for j in range(nXsteps-1):
                    path.append({'X': path[-1]['X'] + XstepSize, 
                                 'Y': path[-1]['Y']})
                    indexPath.append((indexPath[-1][0] + 1,
                                      indexPath[-1][1]))
            else:
                for j in range(nXsteps-1):
                    path.append({'X': path[-1]['X'] - XstepSize, 
                                 'Y': path[-1]['Y']})
                    indexPath.append((indexPath[-1][0] - 1,
                                      indexPath[-1][1]))
            
            path.append({'X': path[-1]['X'], 
                         'Y': path[-1]['Y'] + YstepSize})
            indexPath.append((indexPath[-1][0],
                              indexPath[-1][1] + 1))
        del path[-1]
        del indexPath[-1]
        
        return path, indexPath
    
    def atualizeInterfacePos(self):
        self.emitRelPos.emit(self.getRelPosition())
        if self.dataHandler is not None:
            try:
                curveData = self.dataHandler.getCurveData((self.posRel['Xindex'],\
                                                           self.posRel['Yindex']))
                if curveData is not None:
                    self.emitCurveData.emit(curveData)
            except Exception as erro:
                errorMessage = erro.args[0]
                self.emitError.emit('Error on data handler: '+str(errorMessage))
        else:
            pass
        
    ### RELATIVE MOVEMENT
    
    def getRelPosition(self):
        return self.posRel
    
    def setRelPosition(self, pos):
        self.posRel['X'] = self._roundToAxis(pos['X'], self.scanStepSize['X'])
        self.posRel['Y'] = self._roundToAxis(pos['Y'], self.scanStepSize['Y'])
        self.posRel['Xindex'] = int(self.posRel['X']/self.scanStepSize['X'])
        self.posRel['Yindex'] = int(self.posRel['Y']/self.scanStepSize['Y'])
        
        self.atualizeInterfacePos()
        if self.relMoveLocker == False:
            self.drivePiezo(self.posRel)
        
    def drivePiezo(self, pos):
        self.piezo.moveSample(pos)
        voltX, voltY = self.piezo.getVoltage()
        self.emitVoltageStatus.emit(voltX, voltY)
        
    def moveUp(self):
        curPos = self.getRelPosition()
        newPos = {'X': curPos['X'],
                  'Y': curPos['Y'] + self.scanStepSize['Y']}
        self.setRelPosition(newPos)
    
    def moveDown(self):
        curPos = self.getRelPosition()
        newPos = {'X': curPos['X'],
                  'Y': curPos['Y'] - self.scanStepSize['Y']}
        self.setRelPosition(newPos)
        
    def moveLeft(self):
        curPos = self.getRelPosition()
        newPos = {'X': curPos['X'] - self.scanStepSize['X'],
                  'Y': curPos['Y']}
        self.setRelPosition(newPos)
        
    def moveRight(self):
        curPos = self.getRelPosition()
        newPos = {'X': curPos['X'] + self.scanStepSize['X'],
                  'Y': curPos['Y']}
        self.setRelPosition(newPos)
    
    def moveCenter(self, posCenter):
        self.scanCenter = posCenter
        self.emitCenterPos.emit(self.scanCenter)
     
    def setScanCenter(self):
        """Sets the relative position as the new absolute position to the next scan"""
        NewCenterPos = self.posRel
        if (NewCenterPos['X'] >= self.scanRange['X']/2) \
            and (NewCenterPos['Y'] >= self.scanRange['Y']/2):
            self.moveCenter(NewCenterPos)
            # Emit Message: return ('Center set')
        else:
            self.emitError.emit('The scan size will extrapolate the piezo limits')
    
    # GENERAL
    def saveFile(self, filename, addText):
        """When the 'Save' pushButton is pressed, or 'Ctrl + S': 
            Opens a dialog to save a .hss file"""
        if filename != '':
            scanParams = vars(self.scan)
            #scanParams.update({'notes' : addText})
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                caption="Select File Path",dir=filename,filter="Hyper Spec (*.hss)")
            if fileName:
                try:
                    file = open(fileName, 'wb')
                    pickle.dump(scanParams, file)
                    file.close()
                    return ("File saved successfully")
                except:
                    self.emitError.emit("Error on saving File")
        else:
            self.emitError.emit("Did not save. Please name your file")
    
    def openFile(self):
        """When the Menu->File->Open is pressed, or 'Ctrl + O': 
            Opens a dialog to read a .hss file"""
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            caption="Select File Path",dir="",filter="Hyper Spec (*.hss)")
        if fileName:
            file = open(fileName, 'rb')
            loadedScan = self
            loadedScan.__dic__ = pickle.load(file)
            file.close()
            
            self.scan__dic__ = loadedScan.__dic__
            return self.getScanParams()
