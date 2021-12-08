"""
DialogBox oppened by the Main User Interface. Contains the Spectrometer's specifications
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pickle
import os.path

layout_form_spec = uic.loadUiType("dialogs/spec_dialog.ui")[0]

class spec_dialog(QtWidgets.QDialog, layout_form_spec):
    Ok = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setWindowTitle("Spectrometer System Settings")
        self.loadInfo(self.comboBox.currentText())

        self.pushButton_ok.clicked.connect(self.okPushButton)
        self.pushButton_cancel.clicked.connect(self.cancelPushButton)

    def okPushButton(self):
        self.Ok.emit()
        self.saveInfo(self.comboBox.currentText())
        self.close()

    def cancelPushButton(self):
        self.close()

    def saveInfo(self, specSystem):
        self.parameters = {
            "nDimSpinBox": self.nDimSpinBox.value(),
            "centralWvSpinBox": self.centralWvSpinBox.value(),
            "coverageSpinBox": self.coverageSpinBox.value(),
        }
        filename = specSystem.replace(" ", "")+'.plk'
        try:
            file = open(filename, 'wb')
            pickle.dump(self.parameters, file)
            file.close()
        except:
            QtWidgets.QErrorMessage().showMessage('Error on saving file')

    def loadInfo(self, specSystem):
        if (os.path.isfile("dialogs/"+specSystem.replace(" ", "")+'.plk')):
            filename = specSystem.replace(" ", "")+'.plk'
            try:
                file = open(filename, 'rb')
                self.parameters = pickle.load(file)
                file.close()

                self.nDimSpinBox.setValue(self.parameters["nDimSpinBox"])
                self.centralWvSpinBox.setValue(self.parameters["centralWvSpinBox"])
                self.coverageSpinBox.setValue(self.parameters["coverageSpinBox"])
            except:
                QtWidgets.QErrorMessage().showMessage('Error on saving file')

        else:
            pass
