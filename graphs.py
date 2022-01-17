# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 15:23:13 2021

@author: Allison Pessoa
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from PyQt5 import QtCore

import numpy as np


class ScanMap():
    def __init__(self, promoted_widget, piezoParams):
        self.widget_positioningMap = promoted_widget
        self.widget_positioningMap.setBackground(None)
        
        self.mapPlotItem = self.widget_positioningMap.addPlot()
        self.mapPlotItem.setMouseEnabled(x=False, y=False)
        self.mapPlotItem.hideButtons()
        self.mapPlotItem.showAxes(True)
        
        self.mapPlotItem.setLabel('left', 'Position Y (um)')
        self.mapPlotItem.setLabel('bottom', 'Position X (um)')
        
        self.mapRect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1))
        self.mapRect.setPen(pg.mkPen(0, 0, 0))
        
        self.setTotalRange(piezoParams['totalStrokeUmDoubleSpinBox_x']/1000,
                           piezoParams['totalStrokeUmDoubleSpinBox_y']/1000)
        self.mapPlotItem.addItem(self.mapRect)
        
    def setTotalRange(self, xTotalRange, yTotalRange):
        self.mapPlotItem.setXRange(0 , xTotalRange)
        self.mapPlotItem.setYRange(0 , yTotalRange)
        
    def updatePiezoMap(self, params):
        """Updates the positioning Map"""
        halfX = params["Xrange"]/2
        halfY = params["Yrange"]/2
        
        x0 = (params["Xcenter"] - halfX)/1000
        y0 = (params["Ycenter"] - halfY)/1000
        
        self.mapRect.setRect(x0, y0, params["Xrange"]/1000, params["Yrange"]/1000)

class CurvePlot():
    def __init__(self, promoted_widget):
        self.widget_spectrumPlot = promoted_widget
        self.widget_spectrumPlot.setBackground(None)
        self.curvePlot = self.widget_spectrumPlot.plot()
        self.curvePlot.setPen('k')
    
    def updateCurveData(self, curveData): 
        x, y = curveData
        self.curvePlot.setData(x=x, y=y)


class ImagePlot():
    def __init__(self, promoted_widget):
        self.widget_imagePlot = promoted_widget
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
    
    def getScene(self):
        return self.imagePlot.scene()
    
    def updateCrossLine(self, pos):
        self.crossVLine.setPos(pos['X'])
        self.crossHLine.setPos(pos['Y'])
        
    def updateImageRect(self, params):
        self.updateImageData(np.zeros((params['nXsteps'], params['nYsteps'])))

        self.imagePlot.setRect(params["Xcenter"]-params["Xrange"]/2,\
                               params["Ycenter"]-params["Yrange"]/2,\
                               params["Xrange"],\
                               params["Yrange"])
        
    def updateImageData(self, imageData):
        self.colorBar.setLevels((np.amin(imageData), np.amax(imageData)))
        self.imagePlot.setImage(imageData)