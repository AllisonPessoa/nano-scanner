"""
DialogBox oppened by the Main User Interface in case of error.
"""
from PyQt5 import QtWidgets

class errorBoxAlternative():
    def __init__(self, text):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Critical)
        self.msg.setText("Error")
        self.msg.setInformativeText(text)
        self.msg.setWindowTitle("Error")
        self.msg.addButton(QtWidgets.QMessageBox.Ok)
        self.msg.exec_()
