"""
DialogBox oppened by the Main User Interface. Contains the Piezoelectric System's specifications
"""
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import pickle

import sys, os
import pkg_resources

from logging_setup import getLogger
logger = getLogger()

class PiezoDialog(QtWidgets.QDialog):
    Ok = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        file_layout = 'piezo_dialog.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename(__name__, file_layout)
        loadUi(file_layout_path, self)
        self.setWindowTitle("Piezoelectronic System Settings")

        dir = pkg_resources.resource_filename('instruments.piezosystem', "")
        self.comboBox_piezosName.addItem('defaultPiezo')
        for file in os.listdir(dir):
            if file.endswith(".plk") == 1 and file != "defaultPiezo.plk":
                self.comboBox_piezosName.addItem(file.replace(".plk",""))

        self.comboBox_piezosName.currentIndexChanged.connect(lambda: self.loadInfo(self.comboBox_piezosName.currentText()))
        self.pushButton_setDefaut.clicked.connect(self.setDefaultPiezo)
        self.pushButton_newPiezo.clicked.connect(self.createNewPiezo)
        self.pushButton_ok.clicked.connect(self.okPushButton)
        self.pushButton_cancel.clicked.connect(self.cancelPushButton)

        self.loadInfo('defaultPiezo')

    def setDefaultPiezo(self):
        self.saveInfo('defaultPiezo')
        self.comboBox_piezosName.setCurrentIndex(0)

    def createNewPiezo(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'PiezoSytemName', 'Enter the piezo`s name:')
        if ok:
            self.comboBox_piezosName.addItem(name)
            self.saveInfo(name)
            index = self.comboBox_piezosName.findText(name)
            self.comboBox_piezosName.setCurrentIndex(index)
            logger.info("Piezo " + name + " created.")

    def okPushButton(self):
        self.Ok.emit()
        self.saveInfo(self.comboBox_piezosName.currentText())
        self.close()

    def cancelPushButton(self):
        self.close()

    def getParameters(self):
        parameters = {
        "name": self.lineEdit_PiezosName.text(),
        "IDnumber": self.lineEdit_IDnumber.text(),
        "minDoubleSpinBox_x": self.minDoubleSpinBox_x.value(),
        "minDoubleSpinBox_y": self.minDoubleSpinBox_y.value(),
        "minDoubleSpinBox_z": self.minDoubleSpinBox_z.value(),
        "maxDoubleSpinBox_x": self.maxDoubleSpinBox_x.value(),
        "maxDoubleSpinBox_y": self.maxDoubleSpinBox_y.value(),
        "maxDoubleSpinBox_z": self.maxDoubleSpinBox_z.value(),
        "amplificationSpinBox_x": self.amplificationSpinBox_x.value(),
        "amplificationSpinBox_y": self.amplificationSpinBox_y.value(),
        "amplificationSpinBox_z": self.amplificationSpinBox_z.value(),
        "maxVoltageRateDoubleSpinBox_x": self.maxVoltageRateDoubleSpinBox_x.value(),
        "maxVoltageRateDoubleSpinBox_y": self.maxVoltageRateDoubleSpinBox_y.value(),
        "maxVoltageRateDoubleSpinBox_z": self.maxVoltageRateDoubleSpinBox_z.value(),
        "totalStrokeUmDoubleSpinBox_x": self.totalStrokeUmDoubleSpinBox_x.value(),
        "totalStrokeUmDoubleSpinBox_y": self.totalStrokeUmDoubleSpinBox_y.value(),
        "totalStrokeUmDoubleSpinBox_z": self.totalStrokeUmDoubleSpinBox_z.value(),
        "maxHysteresisSpinBox_x": self.maxHysteresisSpinBox_x.value(),
        "maxHysteresisSpinBox_y": self.maxHysteresisSpinBox_y.value(),
        "maxHysteresisSpinBox_z": self.maxHysteresisSpinBox_z.value(),
        }
        return parameters

    def saveInfo(self, piezoFileDescr):
        parameters = self.getParameters()
        filename = piezoFileDescr + '.plk'
        file_path = pkg_resources.resource_filename('instruments.piezosystem', filename)
        logger.info("Piezo " + piezoFileDescr + " saved successfully.")

        try:
            file = open(file_path, 'wb')
            pickle.dump(parameters, file)
            file.close()
        except:
            QtWidgets.QErrorMessage().showMessage('Error on saving file')

    def loadInfo(self, piezoFileDescr):

        filename = piezoFileDescr + '.plk'
        file_piezo_path = pkg_resources.resource_filename('instruments.piezosystem', filename)

        if (os.path.isfile(file_piezo_path)):
            try:
                file = open(file_piezo_path, 'rb')
                parameters = pickle.load(file)
                file.close()
                self.lineEdit_PiezosName.setText(parameters["name"])
                self.lineEdit_IDnumber.setText(parameters["IDnumber"])
                self.minDoubleSpinBox_x.setValue(parameters["minDoubleSpinBox_x"])
                self.minDoubleSpinBox_y.setValue(parameters["minDoubleSpinBox_y"])
                self.minDoubleSpinBox_z.setValue(parameters["minDoubleSpinBox_z"])
                self.maxDoubleSpinBox_x.setValue(parameters["maxDoubleSpinBox_x"])
                self.maxDoubleSpinBox_y.setValue(parameters["maxDoubleSpinBox_y"])
                self.maxDoubleSpinBox_z.setValue(parameters["maxDoubleSpinBox_z"])
                self.amplificationSpinBox_x.setValue(parameters["amplificationSpinBox_x"])
                self.amplificationSpinBox_y.setValue(parameters["amplificationSpinBox_y"])
                self.amplificationSpinBox_z.setValue(parameters["amplificationSpinBox_z"])
                self.maxVoltageRateDoubleSpinBox_x.setValue(parameters["maxVoltageRateDoubleSpinBox_x"])
                self.maxVoltageRateDoubleSpinBox_y.setValue(parameters["maxVoltageRateDoubleSpinBox_y"])
                self.maxVoltageRateDoubleSpinBox_z.setValue(parameters["maxVoltageRateDoubleSpinBox_z"])
                self.totalStrokeUmDoubleSpinBox_x.setValue(parameters["totalStrokeUmDoubleSpinBox_x"])
                self.totalStrokeUmDoubleSpinBox_y.setValue(parameters["totalStrokeUmDoubleSpinBox_y"])
                self.totalStrokeUmDoubleSpinBox_z.setValue(parameters["totalStrokeUmDoubleSpinBox_z"])
                self.maxHysteresisSpinBox_x.setValue(parameters["maxHysteresisSpinBox_x"])
                self.maxHysteresisSpinBox_y.setValue(parameters["maxHysteresisSpinBox_y"])
                self.maxHysteresisSpinBox_z.setValue(parameters["maxHysteresisSpinBox_z"])

                logger.info("Piezo " + piezoFileDescr + " settings changed successfully.")
            except:
                QtWidgets.QErrorMessage().showMessage('Error on loading file')

        else:
            logger.info("Did not find a Piezo file to load. Nothing changed.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    piezoDlg = PiezoDialog()
    piezoDlg.show()
    sys.exit(app.exec_())
