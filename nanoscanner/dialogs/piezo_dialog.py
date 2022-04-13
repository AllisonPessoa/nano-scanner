"""
DialogBox oppened by the Main User Interface. Contains the Piezoelectric System's specifications
"""
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import pickle

import sys, os
import pkg_resources

class PiezoDialog(QtWidgets.QDialog):
    Ok = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        file_layout = 'piezo_dialog.ui'  # always use slash
        file_layout_path = pkg_resources.resource_filename(__name__, file_layout)
        loadUi(file_layout_path, self)
        
        self.setWindowTitle("Piezoelectronic System Settings")
        self.loadInfo(self.comboBox.currentText())
        self.pushButton_ok.clicked.connect(self.okPushButton)
        self.pushButton_cancel.clicked.connect(self.cancelPushButton)

    def okPushButton(self):
        self.Ok.emit()
        self.saveInfo(self.comboBox.currentText())
        self.close()

    def cancelPushButton(self):
        self.close()
    def getParameters(self):
        parameters = {
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
        filename = piezoFileDescr.replace(" ", "")+'.plk'
        file_path = pkg_resources.resource_filename('instruments.piezosystem', filename)

        try:
            file = open(file_path, 'wb')
            pickle.dump(parameters, file)
            file.close()
        except:
            QtWidgets.QErrorMessage().showMessage('Error on saving file')

    def loadInfo(self, piezoFileDescr):

        filename = piezoFileDescr.replace(" ", "")+'.plk'
        file_piezo_path = pkg_resources.resource_filename('instruments.piezosystem', filename)

        if (os.path.isfile(file_piezo_path)):
            try:
                file = open(file_piezo_path, 'rb')
                parameters = pickle.load(file)
                file.close()

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

            except:
                QtWidgets.QErrorMessage().showMessage('Error on loading file')

        else:
            print("Did not find a Piezo file to load. Loading the default parameters.")
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    piezoDlg = PiezoDialog()
    piezoDlg.show()
    sys.exit(app.exec_())