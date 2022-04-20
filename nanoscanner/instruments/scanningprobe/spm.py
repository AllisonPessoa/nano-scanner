# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Allison Pessoa
"""
import sys
import pkg_resources

#
import numpy as np
import time
from simple_pid import PID

import nidaqmx
from collections import deque

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore

#
from logging_setup import getLogger
logger = getLogger()

from instruments.data_handler import DataHandler, FinalMeta

class ScanningProbe(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
    """ Digital PID Controller"""

    def __init__(self, parent=None):
        super().__init__(parent)
        file_layout = 'spm_layout.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename('instruments.scanningprobe', file_layout)
        loadUi(file_layout_path, self)

        self.lineEdit_Pcontrol.editingFinished.connect(self._updatePIDparams)
        self.lineEdit_Icontrol.editingFinished.connect(self._updatePIDparams)
        self.lineEdit_Dcontrol.editingFinished.connect(self._updatePIDparams)
        self.lineEdit_sampleTime.editingFinished.connect(self._updatePIDparams)

        self.lineEdit_outputMin.editingFinished.connect(self._updatePiezoParams)
        self.lineEdit_outputMax.editingFinished.connect(self._updatePiezoParams)
        self.lineEdit_convFactor.editingFinished.connect(self._updatePiezoParams)

        self.doubleSpinBox_setPoint.valueChanged.connect(self._updateSetPoint)
        self.horizontalSlider_setPoint.sliderMoved.connect(
            lambda: self.doubleSpinBox_setPoint.setValue(
                    self.horizontalSlider_setPoint.value()/10))
        self.doubleSpinBox_setPoint.textChanged.connect(
            lambda: self.horizontalSlider_setPoint.setValue(
                    int(self.doubleSpinBox_setPoint.value()*10)))

        self.lineEdit_stepDelay.editingFinished.connect(self._updateStepDelay)
        self.pushButton_startTracking.clicked.connect(self._startTracking)

    def open(self):
        self._updatePIDparams()
        self._updatePiezoParams()
        self._updateSetPoint()
        self._updateStepDelay()

        self._startAnalogInput()
        self._startAnalogOutput()

    def setDataParams(self, Xdim, Ydim):
        self.dim = (Xdim,Ydim)
        self.imageMap = np.zeros(self.dim)
        self.voltageBuffer = deque([],maxlen=100)
        logger.info("SPM got data params")

    def getDataDuringScan(self, indexPos):
        time.sleep(self.stepDelay) #seconds
        singleValue = self._acquireData()
        self._setPixelData(indexPos, singleValue)

        imageData = self._getIntensityMap()
        curveData = self._getDataBuffer()

        return imageData, curveData

    def getCurveData(self, indexPos):
        return None

    def getRawData(self):
        return self.imageMap

    def close(self):
        self._closeAnalogInput()
        self._closeAnalogOutput()

    ### -------
    def _setPixelData(self, pos, value):
        value = value*self.convFactor
        self.imageMap[pos[0]][pos[1]] = value
        self.voltageBuffer.append(value)
        self.lcdNumber_counterValue.display(value)

    def _getIntensityMap(self):
        return self.imageMap

    def _getDataBuffer(self):
        return (range(len(self.voltageBuffer)),list(self.voltageBuffer))

    def _acquireData(self):
        value = self.task.read()
        return value

    def _startAnalogInput(self):
        try:
            self.taskInput = nidaqmx.Task()
            self.taskInput.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            self.taskInput.start()
            self.label_deviceStatus.setText("Connected.")
            logger.info("Analog Input Started")

        except Exception as erro:
            logger.exception("Error on Starting Analog Input")

    def _closeAnalogInput(self):
        try:
            self.taskInput.stop()
            self.taskInput.close()
            logger.info("SPM Closed analog input")
        except:
            logger.exception("Error on Closing Analog Input")

    def _startAnalogOutput(self):
        try:
            self.taskOutput = nidaqmx.Task()
            self.taskOutput.ao_channels.add_ao_voltage_chan("Dev1/ao0")
            self.taskOutput.start()
            logger.info("SPM - Output Piezo started")

        except Exception:
           logger.exception("Error on starting SPM Piezo Output")

    def _closeAnalogOutput(self):
       try:
           self.taskOutput.stop()
           self.taskOutput.close()
           logger.info("SPM Closed analog output")
       except:
           logger.exception("Error on Closing Analog Output")

    def _updatePIDparams(self):
        self.PID_P = float(self.lineEdit_Pcontrol.text())
        self.PID_I = float(self.lineEdit_Icontrol.text())
        self.PID_D = float(self.lineEdit_Dcontrol.text())
        self.sampleTime = float(self.lineEdit_sampleTime.text())/1000

    def _updatePiezoParams(self):
        self.outputMin = float(self.lineEdit_outputMin.text())
        self.outputMax = float(self.lineEdit_outputMax.text())
        self.convFactor = float(self.lineEdit_convFactor.text())

    def _updateSetPoint(self):
        print('set')
        self.setPoint = self.doubleSpinBox_setPoint.value()

    def _updateStepDelay(self):
        self.stepDelay = float(self.lineEdit_stepDelay.text())/1000

    def _startTracking(self):
        if self.pushButton_startTracking.isChecked() == True:
            self.executionThread = QtCore.QThread()
            self.moveToThread(self.executionThread)
            self.worker = Worker(self.PID_P, self.PID_I, self.PID_D)
            #Starting
            self.startTracking = True
            self.executionThread.started.connect(self._PIDworker)
            self.executionThread.start()

            self.pushButton_startTracking.setStyleSheet("background-color: rgb(255, 170, 127);")
            self.pushButton_startTracking.setText("Stop Tracking")
            logger.info("SPM - PID start tracking")

        else:
            self.startTracking = False
            self.executionThread.quit()
            self._view.finishScan()

            self.pushButton_startMeasurement.setChecked(False)
            self.pushButton_startMeasurement.setStyleSheet("background-color: rgb(170, 255, 127);")
            self.pushButton_startMeasurement.setText("Start Tracking")
            logger.info("SPM - PID stop tracking")

    class Worker(QtCore.QObject):
        def __init__(self, P, I, D, outputMax, outputMin):
            self.P = P
            self.I = I
            self.D = D
            self.outPutMax = outputMax
            self.outPutMin = outputMin

        def _PIDworker(self):
            pid = PID(, setpoint=self.setPoint)
            while True:
                pid.setpoint = self.setPoint
                input = 0
                #input = self.taskInput.read()
                control = pid(input)
                print(control)
                #self.taskOutput.write(control, auto_start=True)
                time.sleep(self.sampleTime)

    ### --------

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    SPM_settings = ScanningProbe()
    SPM_settings.open()
    SPM_settings.show()
    sys.exit(app.exec_())
