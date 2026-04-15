# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:25:27 2021

@author: Nano2
"""
import pkg_resources
import sys
#
import numpy as np

from collections import deque
import serial
import serial.tools.list_ports

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

#
from logging_setup import getLogger
logger = getLogger()

from instruments.data_handler import DataHandler, FinalMeta

class TCSPC(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
    def __init__(self, parent=None):
        super().__init__(parent)

        file_layout = 'TCSPC_layout.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename('instruments.TCSPC', file_layout)
        loadUi(file_layout_path, self)

        self.paired = False
        self.pushButton_updateList.clicked.connect(self._updateListPorts)
        self.pushButton_pair.clicked.connect(self._pairDevice)

        self.radioButton_setHRTIM.clicked.connect(lambda: self._changeTIMERpreesc(self.radioButton_setHRTIM))
        self.radioButton_setTIM.clicked.connect(lambda: self._changeTIMERpreesc(self.radioButton_setTIM))

    def _changeTIMERpreesc(self, radiobuttton):
        if radiobuttton.text() == 'HRTIM':
            self.widget_timParams.setDisabled(True)
            self.widget_HrtimSetRes.setDisabled(False)

        elif radiobuttton.text() == 'TIM':
            self.widget_timParams.setDisabled(False)
            self.widget_HrtimSetRes.setDisabled(True)

    def setDataParams(self, Xdim, Ydim):
        self.dim = (Xdim,Ydim)
        self.hyperData = np.empty(self.dim, dtype=object)
        self.intensityMap = np.zeros(self.dim)

        self._setDeviceParams()
        logger.info("TCSPC got data params")

    def getDataDuringScan(self, indexPos):
        correlation_curve = self._acquireData()
        self._setPixelData(indexPos, correlation_curve)

        imageData = self._getIntensityMap()
        curveData = self.getCurveData(indexPos)

        return imageData, curveData

    def getCurveData(self, indexPos):
        correlation_curve = self.hyperData[indexPos[0], indexPos[1]]
        time = [x*self.plot_time_preesc for x in range(len(correlation_curve))]
        return (time, correlation_curve)

    def getRawData(self):
        return self.hyperData

    def close(self):
        if self.paired == True:
            self.device.write("stop_hrtim\n".encode())
            logger.info("TCSPC Closed")

    def start(self):
        if self.paired == True:
            self._clearBuffer()
            if self.radioButton_setHRTIM.isChecked() == True:
                self.device.write("start_hrtim\n".encode())
                logger.info("TCSPC at HRTIM Started")

            elif self.radioButton_setTIM.isChecked() == True:
                self.device.write("start_tim\n".encode())
                logger.info("TCSPC at TIMx Started")

    ### -------
    def _setPixelData(self, index_pos, value):
        self.hyperData[index_pos[0]][index_pos[1]] = value
        av_value = np.average(value)
        self.lcdNumber_counterValue.display(av_value)
        self.intensityMap[index_pos[0]][index_pos[1]] = av_value

    def _getIntensityMap(self):
        return self.intensityMap

    def _updateListPorts(self):
        self.listPorts = serial.tools.list_ports.comports()

        self.comboBox_serialPort.clear()
        for port in self.listPorts:
            self.comboBox_serialPort.addItem(port.description)

    def _pairDevice(self):
        if  self.pushButton_pair.isChecked() == True:
            if self.comboBox_serialPort.currentText() != 'None':
                portIndex = self.comboBox_serialPort.currentIndex()
                portDevice = self.listPorts[portIndex].device
                portDescription = self.listPorts[portIndex].description
                boudRate = int(self.lineEdit_boudRate.text())

                try:
                    self.device = serial.Serial(portDevice, boudRate, timeout=5, write_timeout=5)
                    self.paired = True
                    self.pushButton_pair.setText("Unpair")
                    self.label_deviceStatus.setText("Connected.")
                    logger.info("Device " + portDescription + "connected.")

                    self._setDeviceParams()

                except Exception as erro:
                    self.paired = False
                    self.pushButton_pair.setChecked(False)
                    errorMessage =  erro.args[0]
                    self.label_deviceStatus.setText("Erro "+ errorMessage)
                    logger.exception("Error on starting device" + portDescription)
        else:
            if self.paired == True:
                self.device.close()
                logger.info("TCSPC Closed")
            self.paired = False
            self.pushButton_pair.setText("Pair")
            self.label_deviceStatus.setText("Disconnected.")

    def _setDeviceParams(self):
        ##### TIM PREESC
        TIM_preesc = str(self.spinBox_TimSetRes.value())

        ##### HRTIM PREESC
        radio_buttons = self.widget_HrtimSetRes.findChildren(QtWidgets.QRadioButton)
        for rb in radio_buttons:
            if rb.isChecked():
                gateTime = rb.text()
        if gateTime == '2.08 ns': HRTIM_preesc = '0'
        elif gateTime == '4.17 ns': HRTIM_preesc = '1'
        elif gateTime == '8.33 ns': HRTIM_preesc = '2'
        self.plot_time_preesc = 1 / (480 / 2 ** (int(HRTIM_preesc)))

        ##### NUMBER OF CYCLES
        cycles = int(self.spinBox_setCycles.value())

        try:
            self.device.reset_output_buffer()

            text = "tim_preesc " + TIM_preesc + "\n"
            self.device.write(text.encode())
            logger.info("TIMx preescale set to: " + str(TIM_preesc) + ' ns')

            text = "hrtim_preesc " + HRTIM_preesc + "\n"
            self.device.write(text.encode())
            logger.info("HRTIM preescale set to: " + str(gateTime))

            text = "trigger_cycle " + str(cycles - 1) + "\n" #(Cycles - 1) because HRTIM arduino needs at least 2 pulses to reset
            self.device.write(text.encode())
            logger.info("Number of cycles set to: " + str(cycles))

            self.label_deviceStatus.setText("Params Set")
        except Exception as erro:
            self._clearBuffer()
            error = erro.args[0]
            self.label_deviceStatus.setText("Error. " + error)
            logger.info("Error. " + error)

    def _clearBuffer(self):
        self.device.reset_input_buffer()
        self.device.reset_output_buffer()

    def _acquireData(self):

        self.device.write("get_hrtim\n".encode()) #if entryLine[0] == 'A':
        expected = 65535 * 4
        raw = self.device.read(expected)

        data = np.frombuffer(raw, dtype='<u4')  # '<u4' = little-endian uint32

        non_zero_data = data[np.nonzero(data)][:-3]

        return non_zero_data

    ### --------

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    CounterSettings = DigitalCounter()
    CounterSettings.show()
    sys.exit(app.exec_())
