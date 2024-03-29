#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 14:23:49 2021

@author: allison
"""
# INSTRUMENTS model is diff
from instruments.piezosystem import piezo_system
from instruments import instruments

from PyQt5 import QtCore

from logging_setup import getLogger
logger = getLogger()

class Model(QtCore.QObject):

    def __init__(self, piezoParams, scanParams):
        super(Model, self).__init__()
        ### POSITIONING ###
        self.pos={"X": 0, "Y": 0,
                  "Xindex": 0, 'Yindex': 0}

        self.posAbs={"X": 0, "Y": 0}
        self.relMoveLocker = True

        self.setScanParams(scanParams)
        self.dataHandler = None
        self.scanAbort = False
        self.recording = False

        ### INSTRUMENTS INIT ###
        self.piezo = piezo_system.PiezoCommunication(piezoParams)
        self.scanModes = instruments.getScanModes()

        ### SAVING ###
        self.lastDir = ''

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
        logger.info("Scan Parameters changed")

    def startScan(self, mode):
        scanPath, indexScanPath = self._calculateSteps() ##Calculate previously the scan path
        totalScanLen = self.scanNumSteps['X']*self.scanNumSteps['Y']

        scanModes = self.getScanModes()
        modeKey = next(x for x in scanModes.keys() if x == mode)
        self.dataHandler = scanModes[modeKey]
        self.dataHandler.setDataParams(self.scanNumSteps['X'], \
                                       self.scanNumSteps['Y'])

        logger.info("Scan Started")

        for index, pos in enumerate(scanPath):
            if self.scanAbort == False:
                try:
                    imageData, curveData = self.dataHandler.getDataDuringScan(indexScanPath[index])
                    self.emitImageData.emit(imageData)
                    self.emitCurveData.emit(curveData)

                except Exception as erro:
                    errorMessage = erro.args[0]
                    self.emitError.emit('Error on acquiring data: '+str(errorMessage))
                    logger.exception("Error on acquiring data")
                    break

                #Update scan position
                self.drivePiezo(pos, saveSecurity=False)
                self.emitProgress.emit((index/totalScanLen)*100)
            else:
                break

        self.setPosition(pos)
        self.atualizeInterfacePos()
        self.finishScan()

    def endApplication(self):
        self.drivePiezo({'X': 0, 'Y': 0})
        self.piezo.close()
        scanModes = self.getScanModes()
        for instrum in scanModes.keys():
            scanModes[instrum].close()

    def finishScan(self):
        self.emitFinished.emit()
        logger.info("Scan finished")

    def _calculateSteps(self):
        path = [{'X': self.scanCenter['X'] -  self.scanRange['X']/2,
                 'Y': self.scanCenter['Y'] -  self.scanRange['Y']/2}]
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
        self.emitRelPos.emit(self.getPosition())
        if self.dataHandler is not None:
            try:
                curveData = self.dataHandler.getCurveData((self.pos['Xindex'],\
                                                           self.pos['Yindex']))
                if curveData is not None:
                    self.emitCurveData.emit(curveData)
            except Exception as erro:
                errorMessage = erro.args[0]
                self.emitError.emit('Error on data handler: '+str(errorMessage))
        else:
            pass

    ### POSITION

    def getPosition(self):
        return self.pos

    def setPosition(self, pos):
        self.pos['X'] = self._roundToAxis(pos['X'], self.scanStepSize['X'])
        self.pos['Y'] = self._roundToAxis(pos['Y'], self.scanStepSize['Y'])

        x_index = int((self.pos['X'] - (self.scanCenter['X'] -  self.scanRange['X']/2))/self.scanStepSize['X'])
        y_index = int((self.pos['Y'] - (self.scanCenter['Y'] -  self.scanRange['Y']/2))/self.scanStepSize['Y'])

        if x_index >= 0 and x_index < self.scanNumSteps['X']\
        and y_index >= 0 and y_index < self.scanNumSteps['Y']:
            self.pos['Xindex'] = x_index
            self.pos['Yindex'] = y_index

        logger.info("Move pointer to x: %f, y: %f", self.pos['X'], self.pos['X'])

        self.atualizeInterfacePos()
        if self.relMoveLocker == False:
            self.drivePiezo(self.pos)

    def drivePiezo(self, pos, saveSecurity=True):
        self.piezo.moveSample(pos, save=saveSecurity)
        voltX, voltY = self.piezo.getVoltage()
        self.emitVoltageStatus.emit(voltX, voltY)

    def moveUp(self):
        curPos = self.getPosition()
        newPos = {'X': curPos['X'],
                  'Y': curPos['Y'] + self.scanStepSize['Y']}
        self.setPosition(newPos)

    def moveDown(self):
        curPos = self.getPosition()
        newPos = {'X': curPos['X'],
                  'Y': curPos['Y'] - self.scanStepSize['Y']}
        self.setPosition(newPos)

    def moveLeft(self):
        curPos = self.getPosition()
        newPos = {'X': curPos['X'] - self.scanStepSize['X'],
                  'Y': curPos['Y']}
        self.setPosition(newPos)

    def moveRight(self):
        curPos = self.getPosition()
        newPos = {'X': curPos['X'] + self.scanStepSize['X'],
                  'Y': curPos['Y']}
        self.setPosition(newPos)

    def moveCenter(self, posCenter):
        self.scanCenter = posCenter
        #self.drivePiezo(self.scanCenter)
        self.emitCenterPos.emit(self.scanCenter)

    def setScanCenter(self):
        """Sets the relative position as the new absolute position to the next scan"""
        NewCenterPos = {}
        NewCenterPos['X'] = self.pos['X']
        NewCenterPos['Y'] = self.pos['Y']

        if (NewCenterPos['X'] >= self.scanRange['X']/2) \
            and (NewCenterPos['Y'] >= self.scanRange['Y']/2):
            self.moveCenter(NewCenterPos)
            logger.info("Center Set to x: %f, y: %f", \
                        NewCenterPos['X'], NewCenterPos['Y'])
        else:
            message = "The scan size will extrapolate the piezo limits"
            self.emitError.emit(message)
            logger.error(message)

    def getCurrentDataHandler(self, mode):
        scanModes = self.getScanModes()
        modeKey = next(x for x in scanModes.keys() if x == mode)
        dataHandler = scanModes[modeKey]
        dataHandler.setDataParams(1,1)
        return dataHandler

    def singleCaptureMode(self, mode):
        dataHandler = self.getCurrentDataHandler(mode)
        try:
            imageData, curveData = dataHandler.getDataDuringScan((0,0))
            if curveData is not None:
                self.emitCurveData.emit(curveData)
        except Exception as erro:
            errorMessage = erro.args[0]
            self.emitError.emit('Error on data handler: '+str(errorMessage))
            logger.exception("Error on acquiring data")

    def startRecordMode(self, mode):
        dataHandler = self.getCurrentDataHandler(mode)
        logger.info("Recording Started")

        while self.recording == True:
            try:
                imageData, curveData = dataHandler.getDataDuringScan((0,0))
                if curveData is not None:
                    self.emitCurveData.emit(curveData)

            except Exception as erro:
                self.recording=False
                errorMessage = erro.args[0]
                self.emitError.emit('Error on acquiring data: '+str(errorMessage))
                logger.exception("Error on acquiring data")
