# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 16:45:11 2022

@author: Allison
"""
from PyQt5 import QtWidgets

import sys
import view
import controller

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    window = view.View()
    control = controller.Controller(window)
    window.show()
    app.exec_()