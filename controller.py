#
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 14:23:10 2021

@author: allison
"""
from os import startfile

from PyQt5.QtWidgets import QMessageBox, QShortcut, QFileDialog
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore

import model

import numpy as np

from logging_setup import getLogger
logger = getLogger()

class Controller():
    """Connects the model and the view. User events are sent to the controller,
    which puts the model to work."""
    def __init__(self, mainWindowWid):
        self._view = mainWindowWid
        
        piezoParams = self._view.piezoDlg.getParameters()
        scanParams = self._view.getScanParams()
        
        self._model = model.Model(piezoParams, scanParams)
        self._view.defineScanModes(self._model.getScanModes())
        self.lastDir = ''
        # Connect signals and slots
        self._connectSignals()
        self._connectShortcuts()
        
    def _connectSignals(self):
        """Connect signals and slots."""
        
        ########################
        ### POSITION CONTROL ###
        ########################
        
        #~Lockers
        self._view.checkBox_lockAbsPosition.stateChanged.connect(self.unlockAbsPosition)
        self._view.checkBox_lockSampleMove.stateChanged.connect(self.unlockRelPosition)
        
        ## Absolute position Control
        #~SpinBoxes
        self._view.currentXAbsolutSpinBox.editingFinished.connect(self.moveCenter)
        self._view.currentYAbsolutMSpinBox.editingFinished.connect(self.moveCenter)

        ## Relative Position Control     
        #~SpinBoxes
        self._view.currentXPositionSpinBox.editingFinished.connect(self.moveBySpin)
        self._view.currentYPositionMSpinBox.editingFinished.connect(self.moveBySpin)
        
        #~MouseClick
        self._view.imagePlot.getScene().sigMouseClicked.connect(self.moveByClick)
        
        ########################
        ### SCAN PROPERTIES ####
        ########################
        
        self._view.rangeXpositionMSpinBox.editingFinished.connect(self.changeScanProperties)
        self._view.XstepsSpinBox.editingFinished.connect(self.changeScanProperties)
        self._view.rangeYpositionMSpinBox.editingFinished.connect(self.changeScanProperties)
        self._view.YstepsSpinBox.editingFinished.connect(self.changeScanProperties)

        #~Buttons
        self._view.pushButton_startMeasurement.clicked.connect(self.startScan)
        self._view.pushButton_exportData.clicked.connect(self.exportData)
        self._view.pushButton_setCenter.clicked.connect(self._model.setScanCenter)
        
        ########################
        ##### MENU ACTIONS #####
        ########################
        #~Shortcuts
        self._view.fileAction_open.setShortcut(QKeySequence('Ctrl+O'))
        self._view.fileAction_exit.setShortcut(QKeySequence('Ctrl+Q'))
        self._view.fileAction_exit.setShortcut(QKeySequence('F1'))
        
        #self._view.fileAction_open.triggered.connect(self.openFile)
        self._view.fileAction_help.triggered.connect(lambda: startfile('help.html'))
            
        self._view.settingsAction_piezo.triggered.connect(self.openPiezoDialog)    
        self._view.piezoDlg.Ok.connect(self.updatePiezoProperties)
        
        ###################
        ##### GENERAL #####
        ###################
        self._view.closeEvent = self.closeEvent
        
        ##################################
        ### CREATED SIGNALS FROM MODEL ###
        ##################################
        
        self._model.emitFinished.connect(self.finishScan)
        self._model.emitCurveData.connect(self._view.updateCurveData)
        self._model.emitImageData.connect(self._view.updateImageData)
        self._model.emitRelPos.connect(self._view.updatePos)
        self._model.emitCenterPos.connect(self._view.updateCenterPos)
        self._model.emitError.connect(self._view.errorBoxAlternative)
        self._model.emitVoltageStatus.connect(self._view.displayVoltage)
        self._model.emitProgress.connect(self._view.updateProgressBar)

    def _connectShortcuts(self):

        self.up_shortcut = QShortcut(QKeySequence("Up"), self._view)
        self.down_shortcut = QShortcut(QKeySequence("Down"), self._view)
        self.left_shortcut = QShortcut(QKeySequence("Left"), self._view)
        self.right_shortcut = QShortcut(QKeySequence("Right"), self._view)
        
        self.up_shortcut.activated.connect(self._model.moveUp)
        self.down_shortcut.activated.connect(self._model.moveDown)
        self.left_shortcut.activated.connect(self._model.moveLeft)
        self.right_shortcut.activated.connect(self._model.moveRight)
        
    ############
    ### SCAN ###
    ############
    
    def startScan(self):
        if self._view.pushButton_startMeasurement.isChecked() == True:
            self.executionThread = QtCore.QThread()
            self._model.moveToThread(self.executionThread)
            #Starting
            mode = self._view.tabWidget_modes.tabText(\
                                 self._view.tabWidget_modes.currentIndex())
            self._model.scanAbort = False
            self._view.startScan()
            self.executionThread.started.connect(lambda: self._model.startScan(mode))
            self.executionThread.start()
            
        else:
            self._model.scanAbort = True
            #TIME
            self.finishScan()
            logger.info("Scan Aborted")
        
    def finishScan(self):
        self.executionThread.quit()
        self._view.finishScan()
        
    def changeScanProperties(self):
        scanParams = self._view.getScanParams()
        
        self._model.setScanParams(scanParams)
        self._view.updateScanLimits()
    
    
    ################
    ### MOVEMENT ###
    ################
    
    def unlockAbsPosition(self):
        disable = self._view.checkBox_lockAbsPosition.isChecked()
        self._view.unlockAbsPosition(disable)
    
    def unlockRelPosition(self):
        locked = self._view.checkBox_lockSampleMove.isChecked()
        self._model.relMoveLocker = locked
        self._model.setPosition(self._model.getPosition())
        
    def moveByClick(self, mouseClickEvent):
        vb = self._view.imagePlot.plotItem.vb
        point = vb.mapToView(mouseClickEvent.pos())
        pos = {'X': point.x(), 'Y': point.y()}
        self._model.setPosition(pos)
    
    def moveBySpin(self):
        pos = {'X': self._view.currentXPositionSpinBox.value(),
               'Y': self._view.currentYPositionMSpinBox.value()}
        self._model.setPosition(pos)
    
    def moveCenter(self):
        centerPos = {'X': self._view.currentXAbsolutSpinBox.value(),
                     'Y': self._view.currentYAbsolutMSpinBox.value()}
        self._model.moveCenter(centerPos)
        self._view.updateScanLimits()
    
    def updatePiezoProperties(self):
        piezoParams = self._view.piezoDlg.getParameters()
        self._model.piezo.updateCalibrParams(piezoParams)
    
    ###############
    ### DIALOGS ###
    ###############
    
    def openPiezoDialog(self):
        """Opens the Piezo Dialog for configuration"""
        self._view.piezoDlg.exec_()

    
    #################
    ### EXPORTERS ###
    #################
    
    def exportColorBarRaw(self, fileName):
        numpyArray = self._model.dataHandler.getRawData()
        np.save(fileName  + '_CBR' + '.npy', numpyArray)
        logger.info("Exported ColorBar Raw Data at " + fileName)
        
    def exportColorBarImage(self, fileName):
        exporter = self._view.imagePlot.getExporter()
        exporter.export(fileName + '_CBI' + '.png')
        logger.info("Exported ColorBar Image file at " + fileName)
        
    def exportCurvePlotRaw(self, fileName):
        index_pos = (self._model.pos['Xindex'], self._model.pos['Yindex'])
        curveRawData = self._model.dataHandler.getCurveData(index_pos)
        np.save(fileName + '_CPR' + '.npy', curveRawData)
        logger.info("Exported CurvePlot Raw Data at " + fileName)
        
    def exportCurvePlotImage(self, fileName):
        exporter = self._view.curvePlot.getExporter()
        exporter.export(fileName + '_CPI' + '.png')
        logger.info("Exported CurvePlot Image at " + fileName)
        
    def exportExpInfo(self, fileName):
        logger.info("Exported Experimental Informations at " + fileName)
        
    def exportData(self):

        options = [self._view.checkBox_exportColorBarRaw,
                   self._view.checkBox_exportColorBarImage,
                   self._view.checkBox_exportCurvePlotRaw,
                   self._view.checkBox_exportCurvePlotImage,
                   self._view.checkBox_exportExpInfo]
        functions = [self.exportColorBarRaw,
                     self.exportColorBarImage,
                     self.exportCurvePlotRaw,
                     self.exportCurvePlotImage,
                     self.exportExpInfo]
        
        exportFileName = self._view.lineEdit_fileNameExport.text()
        fileName, _ = QFileDialog.getSaveFileName(
        caption = "Select File Path",\
        directory = self.lastDir + exportFileName)
            
        if fileName:
            #try:
            
            for op in options:
                if op.isChecked() == 1:
                    functions[options.index(op)](fileName)
            
            self.lastDir = fileName.replace(exportFileName,'')

        
    # def openFile(self):
    #     try:
    #         data = self._model.loadFile()
    #         self._view.loadData(data)
    #     except Exception as erro:
    #         errorMessage =  erro.args[0]
    #         self._view.errorBoxAlternative(errorMessage)
    
    def closeEvent(self, event):
        """When the program is properly closed, this method vanishes the Piezo voltage
        event: QEvent"""
        close = QMessageBox.question(self._view,
                                      "QUIT",
                                      "Are you sure want to stop process?",
                                      QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            self._model.endApplication()
            event.accept()
        else:
            event.ignore()