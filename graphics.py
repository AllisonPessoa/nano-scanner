"""
Configures the Image Plot and the Curve Plot. Manages the interface related graphs and functionalities
"""
from guiqwt.tools import SelectPointTool
from guiqwt._scaler import INTERP_NEAREST
from guiqwt.plot import ImageWidget, CurveWidget
from guiqwt.builder import make

from PyQt5 import QtCore

import pyqtgraph as pg
import numpy as np

class SelectPointToolAlternative(SelectPointTool):#Overriding the method to acquire position
    """Subscribes the existent GuiQwt Tool Method for calling the function to move the sample"""
    MARKER_STYLE_KEY = "marker/cross"
    defaultFilter = None
    def move(self, filter, event):
        if self.marker is None:
            return # if something goes wrong ...
        self.marker.move_local_point_to( 0, event.pos() )
        filter.plot.replot()
        self.last_pos = self.marker.xValue(), self.marker.yValue()
        #Aletrnative
        self.defaultFilter = filter
        self.coordinates = self.get_coordinates()
        self.parent.moveByInterface(self.coordinates[0],self.coordinates[1])
        #self.parent.changeRelXpos(self.coordinates[0])
        #self.parent.changeRelYpos(self.coordinates[1])

    def moveByInterface(self,pos):
        """If one left-clicks inside the color bar, this function is called. 
        Changes the marker position and applies the filter.
        pos: QPoint"""
        if self.marker is None:
            return
        self.marker.set_pos(pos.x(),pos.y())
        if self.defaultFilter != None:
            self.defaultFilter.plot.replot()

class ColorBar():
    """Configures the ImagePlot"""
    def __init__(self, widget_colorBar, toolbar, selection):
        """An Image Plot is created inside the Image Widged. A Toolbar is attached to the Widget.
        widget_colorBar: QWidget
        toolbar: QToolBar
        selection: QTool
        """
        self.widget_colorBar = widget_colorBar
        self.toolbar = toolbar
        self.selection = selection
        
        self.dataMap = np.zeros((11,11))
        #Image Widget
        self.imageWidget = ImageWidget(self.widget_colorBar, xlabel=('X Position'),
                                        ylabel=('Y Position'), xunit=('nm'),
                                        yunit=('nm'), yreverse = False)#imageWidget's parent = guiqwt.plot
        self.imageWidget.add_toolbar(self.toolbar, "default")
        self.imageWidget.add_tool(self.selection)
        #self.imageWidget.register_standard_tools()
        self.imageWidget.register_all_image_tools()
        self.selectionTool = self.imageWidget.get_tool(self.selection)
        self.imageWidget.set_default_tool(self.selectionTool)
        self.imageWidget.activate_default_tool()
        #Image Item
        self.item = make.image(self.dataMap) # item = image.ImageItem
        self.item.set_interpolation(INTERP_NEAREST)#avoid graph interpolation
        #Image PLot
        self.plot = self.imageWidget.get_plot() #plot => plot.ImagePlot -> CurvePlot
        self.plot.add_item(self.item)#Adiciona o item ao Plot
        self.imageWidget.set_default_plot(self.plot)
        self.imageWidget.resize(self.widget_colorBar.size())#constrained_layout
        self.imageWidget.show()
    
    def setImage(self, imageData):
        imageData = np.transpose(imageData)
        self.item.set_data(imageData)
        self.plot.update_colormap_axis(self.item)
        self.plot.replot()
    
    # def setPointData(self, pos, pointValue):
    #     self.dataMap[pos[0]][pos[1]] = pointValue
    #     imageData = np.transpose(self.dataMap)
    #     self.item.set_data(imageData)
    #     self.item.set_lut_range([np.amin(imageData),np.amax(imageData)])
    #     self.plot.update_colormap_axis(self.item)
    #     self.plot.replot()
        
    def updateLimits(self, scanParams):
        """Updates limits, bounds, and borders of image plot"""
        self.item.xmin = scanParams['Xcenter'] - scanParams['Xrange']/2
        self.item.xmax = scanParams['Xcenter'] + scanParams['Xrange']/2
        self.item.ymin = scanParams['Ycenter'] - scanParams['Yrange']/2
        self.item.ymax = scanParams['Ycenter'] + scanParams['Yrange']/2
        self.item.update_bounds()
        self.item.update_border()
        self.plot.do_autoscale()        

class Spectrum():
    """Configures the CurvePlot"""
    def __init__(self, widget_spectrum):
        """An Curve Plot is created inside the Curve Widged.
        widget_colorBar: QWidget
        """
        self.widget_spectrum = widget_spectrum
        self.data =  range(100) #Initial data, arbitrary
        #Curve widget
        self.plotWidget = CurveWidget(self.widget_spectrum, xlabel=('Wavelength'),
                                                ylabel=('Intensity'), xunit=('nm'),
                                                yunit=('a.u'))
        #Curve item
        self.item = make.curve(np.asarray(range(len(self.data))),np.asarray(self.data))
        #Curve plot
        self.plot = self.plotWidget.get_plot()
        self.plot.add_item(self.item)
        self.plotWidget.resize(self.widget_spectrum.size())
        self.plotWidget.show()

    def setData(self, data):
        """Updates the curve plot.
        data: list"""
        #try:
        self.item.set_data(range(len(data)), data)
        #except:
        #    pass
        self.plot.do_autoscale()
        self.plot.replot()

class ScanMap():
    """Configures the Positioning Map"""
    def __init__(self, widget_positioningMap, piezoParams):
        """A Positioning Map is created inside the Curve Widged.
        widget_colorBar: QWidget
        """
        self.totalXstroke = piezoParams['totalStrokeUmDoubleSpinBox_x']
        self.totalYstroke = piezoParams['totalStrokeUmDoubleSpinBox_y']

        self.widget_positioningMap = widget_positioningMap
        #Curve widget
        self.plotWidget = CurveWidget(self.widget_positioningMap, xunit=('um'), yunit=('um'))
        
        #Curve plot
        self.plot = self.plotWidget.get_plot()
        self.plot.set_axis_limits("bottom", 0, self.totalXstroke/1000)
        self.plot.set_axis_limits("left", 0, self.totalYstroke/1000)
        #Curve item
        self.rec = make.rectangle(0,10,10,0)#, color='red')

        self.plot.add_item(self.rec)
        
        self.plotWidget.resize(self.widget_positioningMap.size())
        self.plotWidget.show()  

    def updatePosition(self, scanParams):
        """Updates the positioning Map"""
        halfX = scanParams["Xrange"]/2
        halfY = scanParams["Yrange"]/2
        
        x1 = (scanParams["Xcenter"] - halfX)/1000
        x2 = (scanParams["Xcenter"] + halfX)/1000
        y2 = (scanParams["Ycenter"] - halfY)/1000
        y1 = (scanParams["Ycenter"] + halfY)/1000
        
        self.rec.set_rect(x1,y1,x2,y2)
        self.plot.replot()
        
class Spectrum2():
    """Configures the CurvePlot"""
    def __init__(self, layoutForm):
        self.plotWidget = pg.PlotWidget()  ## giving the plots names allows us to link their axes together
        layoutForm.addWidget(self.plotWidget)
        
        self.plotWidget.setBackground('w')
        self.curve = self.plotWidget.plot()
        self.curve.setPen('k')
        
            ## Start a timer to rapidly update the plot in pw
        t = QtCore.QTimer()
        t.timeout.connect(self.updateData)
        t.start(50)
        #updateData()
        
    def rand(self,n):
        data = np.random.random(n)
        data[int(n*0.1):int(n*0.13)] += .5
        data[int(n*0.18)] += 2
        data[int(n*0.1):int(n*0.13)] *= 5
        data[int(n*0.18)] *= 20
        data *= 1e-12
        return data, np.arange(n, n+len(data)) / float(n)

    def updateData(self):
        yd, xd = self.rand(10000)
        print(yd[0])
        self.curve.setData(y=yd, x=xd)
    
class ColorBar2():
    def __init__(self, layoutForm):
        self.plotWidget = pg.PlotWidget(name='Plot1')  ## giving the plots names allows us to link their axes together
        layoutForm.addWidget(self.plotWidget)
        
        self.plotWidget.setBackground('w')
        self.image = pg.ImageItem()
        self.plotWidget.addItem(self.image)
        
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.image)
        self.plotWidget.addItem(self.hist)
        
        self.plotWidget.setLabel('left', 'Position Y', units='nm')
        self.plotWidget.setLabel('bottom', 'Position X', units='nm')
    
    def setData(self, data):
        self.image.setImage(data)
        self.hist.setLevels(data.min(), data.max())

if __name__ == "__main__":
    from PyQt5 import QtGui
    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()
    mw.setWindowTitle('pyqtgraph example: PlotWidget')
    mw.resize(800,800)
    cw = QtGui.QWidget()
    mw.setCentralWidget(cw)
    l = QtGui.QVBoxLayout()
    cw.setLayout(l)

    spectrum = Spectrum2(l)
    mw.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
