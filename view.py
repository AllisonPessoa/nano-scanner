# # -*- coding: utf-8 -*-
# """
# Created on July 2019

# @author: Allison Pessoa
# """

#Interface
from PyQt5 import QtCore, QtWidgets, uic
layout_form = uic.loadUiType("mainLayout.ui")[0]

#Graphics
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import numpy as np

#Dialogs
import sys
import os.path

sys.path.append(os.path.abspath("dialogs"))
import piezo_dialog
import errorBox

#Controller
import controller

#Logger
import logging_setup
logger = logging_setup.getLogger()

class View(QtWidgets.QMainWindow, layout_form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.setupUi(self)
        
        ### AUXILIAR DIALOGS ###
        self.piezoDlg = piezo_dialog.PiezoDialog()
        self.errorBoxAlternative = errorBox.errorBoxAlternative

        ### STATUSBAR ###
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Welcome!")
        
        ### GRAPHICS ###
        self.startCurvePlot()
        self.startImagePlot()
        self.startScanMap()
        
        self.updateScanLimits()
        
        logger.info("Starting GUI")
    
    ###############################
    ### LOCK / UNLOCK INTERFACE ###
    ###############################
    def unlockAbsPosition(self, disabled):
        """Activate or Deactivate the spinboxes and sliders responsible for 
        Center Position Control"""
        self.currentXAbsolutSpinBox.setDisabled(disabled)
        self.currentYAbsolutMSpinBox.setDisabled(disabled)
    
    def lockInterface(self, disabled = False):
        """Lock/Unlock most of the interface widgets"""
        self.lockedUI = disabled
        #~pushButtons
        self.pushButton_save.setDisabled(disabled)
        #~SpinBoxes
        self.rangeXpositionMSpinBox.setDisabled(disabled)
        self.XstepsSpinBox.setDisabled(disabled)
        self.rangeYpositionMSpinBox.setDisabled(disabled)
        self.YstepsSpinBox.setDisabled(disabled)
        self.currentXPositionSpinBox.setDisabled(disabled)
        self.currentYPositionMSpinBox.setDisabled(disabled)
        #~Sliders
        self.horizontalSlider_curXpos.setDisabled(disabled)
        self.horizontalSlider_curYpos.setDisabled(disabled)
        #checkbox
        self.checkBox_lockAbsPosition.setDisabled(disabled)
    
    #######################
    ### GENERAL SETTERS ###
    #######################
    def errorBoxShow(self, message):
        """Show an error box with the message to the user"""
        self.errorBoxAlternative(message)
        
    def updateProgressBar(self, percent):
        """Actualize the progress bar with percent value"""
        self.progressBar_scan.setValue(percent)
    
    def displayVoltage(self, volt_x, volt_y):
        """Display the applied voltage on the LCDs."""
        self.lcdNumber_XVoltage.display(volt_x)
        self.lcdNumber_YVoltage.display(volt_y)

    ###################
    ### POSITIONING ###
    ###################
    
    #Center Position
    def updateCenterPos(self, pos):
        """Update the Center Position Control widgets and Image Plot
        - pos: dict containing 'X' and 'Y' keys"""
        self.horizontalSlider_curXabs.setValue(pos['X'])
        self.currentXAbsolutSpinBox.setValue(pos['X'])
        
        self.horizontalSlider_curYabs.setValue(pos['Y'])
        self.currentYAbsolutMSpinBox.setValue(pos['Y'])

    #Sample Position
    def updatePos(self, pos):
        """Update the Sample Position Control widgets and Image Plot
        - pos: dict containing 'X' and 'Y' keys"""
        self.horizontalSlider_curXpos.setValue(pos['X'])
        self.horizontalSlider_curYpos.setValue(pos['Y'])

        self.currentXPositionSpinBox.setValue(pos['X'])
        self.currentYPositionMSpinBox.setValue(pos['Y'])
        
        #cross line indicating the relative position
        self.crossVLine.setPos(pos['X'])
        self.crossHLine.setPos(pos['Y'])
    
    ############
    ### SCAN ###
    ############
    
    def defineScanModes(self, scanModes):
        """Update the acquisition mode widgets 
        - scanModes: dict with widget objects"""
        for names in scanModes.keys():
            self.tabWidget_modes.addTab(scanModes[names], names)
    
    def getScanParams(self):
        """Oraganize the scan parameters in a dict and return it"""
        parameters = {
        "Xrange": self.rangeXpositionMSpinBox.value(),
        "nXsteps": self.XstepsSpinBox.value(),
        "XstepSize": int(self.rangeXpositionMSpinBox.value()/\
                          self.XstepsSpinBox.value()),
        "Xcenter": self.currentXAbsolutSpinBox.value(),
        
        "Yrange": self.rangeYpositionMSpinBox.value(),
        "nYsteps": self.YstepsSpinBox.value(),
        "YstepSize": int(self.rangeYpositionMSpinBox.value()/\
                          self.YstepsSpinBox.value()),
        "Ycenter": self.currentYAbsolutMSpinBox.value()
        }
        return parameters
    
    def updateScanLimits(self):
        """Update the maximim and minimum values for the scan parameters setters
        and update """
        params = self.getScanParams()
        #
        self.horizontalSlider_curXpos.setMaximum(params["Xcenter"] + params["Xrange"]/2)
        self.horizontalSlider_curXpos.setMinimum(params["Xcenter"] - params["Xrange"]/2)
        self.currentXPositionSpinBox.setMaximum(params["Xcenter"] + params["Xrange"]/2)
        self.currentXPositionSpinBox.setMinimum(params["Xcenter"] - params["Xrange"]/2)
        
        self.horizontalSlider_curYpos.setMaximum(params["Ycenter"] + params["Yrange"]/2)
        self.horizontalSlider_curYpos.setMinimum(params["Ycenter"] - params["Yrange"]/2)
        self.currentYPositionMSpinBox.setMaximum(params["Ycenter"] + params["Yrange"]/2)
        self.currentYPositionMSpinBox.setMinimum(params["Ycenter"] - params["Yrange"]/2)
        
        self.horizontalSlider_curXpos.setSingleStep(int(params["XstepSize"]))
        self.horizontalSlider_curYpos.setSingleStep(int(params["YstepSize"]))
        self.currentXPositionSpinBox.setSingleStep(int(params["XstepSize"]))
        self.currentYPositionMSpinBox.setSingleStep(int(params["YstepSize"]))
        #Avoid ScanRange extrapolate the borders
        self.rangeXpositionMSpinBox.setMaximum(params["Xcenter"]*2)
        self.rangeYpositionMSpinBox.setMaximum(params["Ycenter"]*2)
        #Avoid overlay of steps
        self.XstepsSpinBox.setMaximum(int(params["Xrange"]))
        self.YstepsSpinBox.setMaximum(int(params["Yrange"]))
        
        self.label_xStepSize.setText('X Step Size: %.2f nm'%params["XstepSize"])
        self.label_yStepSize.setText('Y Step Size: %.2f nm'%params["YstepSize"])
        
        #Graphs
        self.updateImageRect(params)
        self.updatePiezoMap(params)
        
        self.statusBar.showMessage("Limits Updated")
        logger.info("Scan Limits Updated")
        
    def startScan(self):
        """Lock interface and change start pushButton status to allow abortion"""
        self.lockInterface(True)
        self.pushButton_startMeasurement.setStyleSheet("background-color: rgb(255, 170, 127);")
        self.pushButton_startMeasurement.setText("Abort Measurement")
        self.statusBar.showMessage("Scan in running")
    
    def finishScan(self):
        """Unlock interface and change start pushButton status to allow start again"""
        self.lockInterface(False)
        self.pushButton_startMeasurement.setChecked(False)
        self.pushButton_startMeasurement.setStyleSheet("background-color: rgb(170, 255, 127);")
        self.updateProgressBar(0)
        self.pushButton_startMeasurement.setText("Start Measurement")
        self.statusBar.showMessage("Measurement finished")
        
    ##############
    ### GRAPHS ###
    ##############
    
    #SCAN MAP
    def startScanMap(self):
        self.widget_positioningMap.setBackground(None)
        self.mapPlotItem = self.widget_positioningMap.addPlot()
        self.mapPlotItem.setMouseEnabled(x=False, y=False)
        self.mapPlotItem.hideButtons()
        
        piezoParams = self.piezoDlg.getParameters()
        self.mapPlotItem.setXRange(0,piezoParams['totalStrokeUmDoubleSpinBox_x'])
        self.mapPlotItem.setYRange(0,piezoParams['totalStrokeUmDoubleSpinBox_y'])
        self.mapPlotItem.showAxes(True)
        
        self.plotItem.setLabel('left', 'Position Y (um)')
        self.plotItem.setLabel('bottom', 'Position X (um)')
        
        self.mapRect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1))
        self.mapRect.setPen(pg.mkPen(0, 0, 0))
        self.mapPlotItem.addItem(self.mapRect)
    
    def updatePiezoMap(self, params):
        """Updates the positioning Map"""
        halfX = params["Xrange"]/2
        halfY = params["Yrange"]/2
        
        x0 = (params["Xcenter"] - halfX)/1000
        y0 = (params["Ycenter"] - halfY)/1000
        
        self.mapRect.setRect(x0, y0, params["Xrange"]/1000, params["Yrange"]/1000)
    
    #CURVE PLOT
    def startCurvePlot(self):
        self.widget_spectrumPlot.setBackground(None)
        self.curvePlot = self.widget_spectrumPlot.plot()
        self.curvePlot.setPen('k')
    
    def updateCurveData(self, curveData):     
        self.curvePlot.setData(curveData)
        QtWidgets.QApplication.processEvents()
    
    #IMAGE PLOT
    def startImagePlot(self):
        self.widget_imagePlot.setBackground(None)
        
        self.plotItem = self.widget_imagePlot.addPlot()
        self.plotItem.setMouseEnabled(x=False, y=False)

        self.imagePlot = pg.ImageItem(np.zeros((10,10)))
        self.plotItem.addItem(self.imagePlot)
        
        self.plotItem.setLabel('left', 'Position Y (nm)')
        self.plotItem.setLabel('bottom', 'Position X (nm)')

        ### ColorMap
        cmap = pg.colormap.get('viridis', source='matplotlib')
        self.colorBar = pg.ColorBarItem(interactive=False, colorMap = cmap)
        self.colorBar.setImageItem(self.imagePlot, insert_in = self.plotItem)
        
        ### Cross Hair
        self.crossVLine = pg.InfiniteLine(pos = 0, angle=90, pen='k', movable=True)
        self.crossHLine = pg.InfiniteLine(pos = 0, angle=0, pen='k', movable=True)
        self.plotItem.addItem(self.crossVLine, ignoreBounds=True)
        self.plotItem.addItem(self.crossHLine, ignoreBounds=True)
        
    def updateImageRect(self, params):
        self.updateImageData(np.zeros((params['nXsteps'], params['nYsteps'])))

        self.imagePlot.setRect(params["Xcenter"]-params["Xrange"]/2,\
                               params["Ycenter"]-params["Yrange"]/2,\
                               params["Xrange"],\
                               params["Yrange"])
        
    def updateImageData(self, imageData):
        self.colorBar.setLevels((np.amin(imageData), np.amax(imageData)))
        self.imagePlot.setImage(imageData)
        
        QtWidgets.QApplication.processEvents()
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = View()
    control = controller.Controller(window)
    window.show()
    app.exec_()
