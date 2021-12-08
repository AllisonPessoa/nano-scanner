"""
The main class of the program: Controls all User Interface and share information between other classes.
Interface the instruments, graphics, and the Worker Thread.

=======================================================================================================

"""

#Interface
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QKeySequence
layout_form = uic.loadUiType("layout.ui")[0]

# Graphics
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
import logging_setup
logger = logging_setup.getLogger()

class View(QtWidgets.QMainWindow, layout_form):
    """Implements  the apps' GUI by hosting all widgets needed to interact
    with the application"""
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.setupUi(self)
        
        #Auxiliar Dialogs
        self.piezoDlg = piezo_dialog.PiezoDialog()
        self.errorBoxAlternative = errorBox.errorBoxAlternative
        
        ### STATUSBAR ###
        self.statusBar =QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Welcome!")
        logger.info("Starting GUI")
        
        ### GRAPHICS ###
        self.startCurvePlot()
        self.startImagePlot()
        self.startScanMap()
        self.updateScanLimits()
        
        ### SHOTCUTS ###
        self.fileAction_open.setShortcut(QKeySequence('Ctrl+O'))
        self.fileAction_save.setShortcut(QKeySequence('Ctrl+S'))
        self.fileAction_exit.setShortcut(QKeySequence('Ctrl+Q'))
        self.fileAction_exit.setShortcut(QKeySequence('F1'))
        
        self.up_shortcut = QtWidgets.QShortcut(QKeySequence("Up"), self)
        self.down_shortcut = QtWidgets.QShortcut(QKeySequence("Down"), self)
        self.left_shortcut = QtWidgets.QShortcut(QKeySequence("Left"), self)
        self.right_shortcut = QtWidgets.QShortcut(QKeySequence("Right"), self)

    
    ### LOCK / UNLOCK METHODS ###
    def unlockAbsPosition(self, disable):
        """Activates or Deactivates the spinboxes and sliders responsible for 
        Absolute Position Control, depending on the state of 'Lock' checkbox"""
        self.currentXAbsolutSpinBox.setDisabled(disable)
        self.currentYAbsolutMSpinBox.setDisabled(disable)
    
    def lockInterface(self, disabled = False):
        """Locks/unlocks interface when the measurement routine start/stop"""
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
        """Shows the error box dialog configured in errorbox.py. 
        This method is connected by a QtSignal from the Worker Thread"""
        self.errorBoxAlternative(message)
        
    def updateProgressBar(self, percent):
        """Actualize the progress bar from 0% to 100%.
        This method is connected by a QtSignal from the Worker Thread"""
        self.progressBar_scan.setValue(percent)
    
    def displayVoltage(self, volt_x, volt_y):
        """Display the voltagen on the LCD."""
        self.lcdNumber_XVoltage.display(volt_x)
        self.lcdNumber_YVoltage.display(volt_y)

    ###################
    ### POSITIONING ###
    ###################
    
    #Absolute Positioning
    def updateCenterPos(self, pos):
        """It is actioned by Absolute Position Control (slides or spinboxes).
        text: 'slider' or 'spinBox'."""
        self.horizontalSlider_curXabs.setValue(pos['X'])
        self.currentXAbsolutSpinBox.setValue(pos['X'])
        
        self.horizontalSlider_curYabs.setValue(pos['Y'])
        self.currentYAbsolutMSpinBox.setValue(pos['Y'])
        
        self.updateScanLimits()

    #Relative Positioning
    def updateRelPos(self, pos):
        """Change the Relative Positioning Control system
        value: position in nm"""
        self.horizontalSlider_curXpos.setValue(pos['X'])
        self.currentXPositionSpinBox.setValue(pos['X'])
        self.crossVLine.setPos(pos['X'])

        self.horizontalSlider_curYpos.setValue(pos['Y'])
        self.currentYPositionMSpinBox.setValue(pos['Y'])
        self.crossHLine.setPos(pos['Y'])
    
    ############
    ### SCAN ###
    ############
    
    def defineScanModes(self, scanModes):
        for names in scanModes.keys():
            self.tabWidget_modes.addTab(scanModes[names], names)
    
    def getScanParams(self):
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
        """Avoid improper values for scan"""
        params = self.getScanParams()
        self.horizontalSlider_curXpos.setMaximum(params["Xcenter"] + params["Xrange"]/2)
        self.horizontalSlider_curXpos.setMinimum(params["Xcenter"] - params["Xrange"]/2)
        self.currentXPositionSpinBox.setMaximum(params["Xcenter"] + params["Xrange"]/2)
        self.currentXPositionSpinBox.setMinimum(params["Xcenter"] - params["Xrange"]/2)
        
        self.horizontalSlider_curYpos.setMaximum(params["Ycenter"] + params["Yrange"]/2)
        self.horizontalSlider_curYpos.setMinimum(params["Ycenter"] - params["Yrange"]/2)
        self.currentYPositionMSpinBox.setMaximum(params["Ycenter"] + params["Yrange"]/2)
        self.currentYPositionMSpinBox.setMinimum(params["Ycenter"] - params["Yrange"]/2)
        
        #
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
        
        self.vanishImage(params['nXsteps'], params['nYsteps'])
        self.updateImageLimits(params)
        
        self.updateMapRect(params)
        
        self.statusBar.showMessage("Limits Updated")
        logger.info("Scan Limits Updated")
        
    def startScan(self):
        self.lockInterface(True)
        self.pushButton_startMeasurement.setStyleSheet("background-color: rgb(255, 170, 127);")
        self.pushButton_startMeasurement.setText("Abort Measurement")
        self.statusBar.showMessage("Scan in running")
    
    def finishScan(self):
        self.lockInterface(False)
        self.pushButton_startMeasurement.setChecked(False)
        self.pushButton_startMeasurement.setStyleSheet("background-color: rgb(170, 255, 127);")
        self.updateProgressBar(0)
        self.pushButton_startMeasurement.setText("Start Measurement")
        self.statusBar.showMessage("Measurement finished")
        
        params = self.getScanParams()
        self.updateImageLimits(params)
        
    ##############
    ### GRAPHS ###
    ##############
    
    #SCAN MAP
    def startScanMap(self):
        self.widget_positioningMap.setBackground(None)
        self.mapPlotItem = self.widget_positioningMap.addPlot()
        self.mapPlotItem.setMouseEnabled(x=False, y=False)
        self.mapPlotItem.hideButtons()
        self.mapPlotItem.setXRange(0,63)
        self.mapPlotItem.setYRange(0,63)
        self.mapPlotItem.showAxes(True)
        self.plotItem.setLabel('left', 'Position Y (um)')
        self.plotItem.setLabel('bottom', 'Position X (um)')
        
        self.mapRect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1))
        self.mapRect.setPen(pg.mkPen(0, 0, 0))
        self.mapPlotItem.addItem(self.mapRect)
    
    def updateMapRect(self, params):
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
        
    def updateImageLimits(self, params):
        self.imagePlot.setRect(params["Xcenter"]-params["Xrange"]/2,\
                               params["Ycenter"]-params["Yrange"]/2,\
                               params["Xrange"],\
                               params["Yrange"])

    def updateImageData(self, imageData):
        self.colorBar.setLevels((np.amin(imageData), np.amax(imageData)))
        self.imagePlot.setImage(imageData)
        
        QtWidgets.QApplication.processEvents()
    
    def vanishImage(self, xSteps, ySteps):
        self.imagePlot.setImage(np.zeros((xSteps, ySteps)))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = View()
    control = controller.Controller(window)
    window.show()
    app.exec_()
