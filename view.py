# # -*- coding: utf-8 -*-
# """
# Created on July 2019

# @author: Allison Pessoa
# """
import sys
import os.path

#Interface
from PyQt5 import QtWidgets, uic
layout_form = uic.loadUiType("mainLayout.ui")[0]

#Graphics
import graphs

#Dialogs
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
        self.scanMapPlot = graphs.ScanMap(self.widget_positioningMap,
                                          self.piezoDlg.getParameters())
        
        self.curvePlot = graphs.CurvePlot(self.widget_spectrumPlot)
        
        self.imagePlot = graphs.ImagePlot(self.widget_imagePlot)
        
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
        
        self.updateScanLimits()

    #Sample Position
    def updatePos(self, pos):
        """Update the Sample Position Control widgets and Image Plot
        - pos: dict containing 'X' and 'Y' keys"""
        self.horizontalSlider_curXpos.setValue(pos['X'])
        self.horizontalSlider_curYpos.setValue(pos['Y'])

        self.currentXPositionSpinBox.setValue(pos['X'])
        self.currentYPositionMSpinBox.setValue(pos['Y'])
        
        self.imagePlot.updateCrossLine(pos)
    
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
        self.imagePlot.updateImageRect(params)
        self.scanMapPlot.updatePiezoMap(params)
        
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
    
    def updateCurveData(self, curveData):     
        self.curvePlot.updateCurveData(curveData)
        QtWidgets.QApplication.processEvents()
    
    def updateImageData(self, imageData):
        self.imagePlot.updateImageData(imageData)
        QtWidgets.QApplication.processEvents()
    
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    window = View()
    control = controller.Controller(window)
    window.show()
    app.exec_()
