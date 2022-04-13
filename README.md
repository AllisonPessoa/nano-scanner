# NanoScanner

## Overview

NanoScanner is an environment to perform scan imaging of micro and nanosystems. It executes sample pixel-by-pixel scan, with nanometric spatial resolution, while acquires information from any desired peripheral instrument that is interacting with the nanosystem. This brings the versatility of building images from numerous physical parameters. Applications performed with the Software includes:
* Luminescence image of single micro and nanoparticles (the detected signal is a photocounter counts)
* Hyperspectral image of single micro and nanoparticles (the detected signal is an entire spectrum by a spectrometer)
* Topography image by SPM (Scanning Probe Microscopy) setup (the detected signal is the frequency shift of the tuning fork that interacts with the sample)
* Scanning Near-field Optical Microscoy (SNOM) (the detected signal is the near-field light - by photodetectors or spectrometers, which is interacting with the scanning tip)
* Among others

NanoScanner provides the versatility of easily implementing new instruments and their controls for acquiring data, which means that NanoScanner's heart is the accurate position control in nanoscale in synchronization with data acquisition. A piezoelectric system controls the sample position in three axis. To provide the necessary voltage to drive the piezo, this software interfaces with a Digital-to-Analog converter (DAC) (National Instruments) which is connected to a ultra-stable voltage amplifier.

Originally, this software was developed for imaging rare-earth-doped dielectric nanoparticles interacting with light. Thus, the built-in peripherals are specific for communicating with the instruments available in our Laboratories, which are:

* **National Instruments ADC (Analog-to-Digital Converter)**: Reads the analog output from a home-assembled photon counter, which counts the number of incoming pulses from the photodetector and transforms it to a voltage level. Also can be used to read the output of a Lock-in amplifier in the Scanning Probe Microscope, which represents que distance of the to the sample, allowing builiding nanoscopic tophography images.

* **Princeton Instruments Monochomator + Andor Solis CCD camera**: This is a typical spectrometer setup for acquiring the spectrum of the particles. The monochomator is responsible for splitting the white light into the CCD camera's sensors. The internal control of both is possible with Python (See pylablib? library), but requires a thorough understanding of the instrument's internal functions and workflows for correctly operating, otherwise could damage the hardware. A more secure approach is to use the manufacture's software for taking the spectra automatically, and constantly, then saving them in a folder (this is possible with the camera's internal programming language), which the scanning routine will be constantly monitoring for new data. When the spectrum file is modified, the routine take that as a pixel's information, and move for the next.

## Installation

Clone this repository on GitHub or Download Zip.

### Dependencies

nidaqmx==0.5.7
numpy==1.18.4+mkl
PyQt5==5.15.6
pyqtgraph==0.12.3
pyserial==3.5

## Documentation

NanoScanner features Widgets Tool Tips, which means that when one places the mouse onto an object (e.g. Text Lines, Check Boxes, etc.), it shows a small text with important information heading the correct usage of the widget.

### Positioning Control

The positioning control is responsible for moving the sample through the space in the three cartesian directions. A coarse movement is adjusted by changing the scan center, while a fine movement is set either by clicking on the Image Plot or by pressing the arrow buttons on keyboard (top, bottom, left, right for 2D positioning on the same Z-plane, ~~and pgUp, pgDn for modifying the Z position~~). The range of the fine movement and the step size are defined in the scan properties panel. Once this properties are changes, the current image is lost and a new empty image is shown. 

There are lockers to the movement in order to keep it safe. If the 'Locker Rel Movement' checkBoxe is checked, the software will not drive voltage to the piezo, but the positioning system still works and the corresponding pixel's data are still showed (If the scan data is hyperspectral).

The specifications of the piezo voltage driving can be set through a dialog in Menu Settings -> Piezoelectric System. More information in Dialogs.

### Peripherals Control

The interfaces with new instruments can be easily implemented because all the source code is written in Python and the peripheral programming is detached from the whole positioning control and Graphical User Interface, only requiring inheritance of classes and implementing some predefined functions. 

To create a new instrument, you must to create a new class with the predefined architecture that it is a child class from DataHandler and QtWidgets.QWidget from PyQt5. Also, the metaclass has to be set as class FinalMeta. To add user-interface configurations of your instrument and show status, for example, you also have to create a small GUI with the necesary constrols and displays. This is done by creating a new QWidget Form in QtDesigner ('.ui' file), with dimensions of W: 230 pixels and H: 310 pixels. Place therein the necessary toolboxes and widgets and save the .ui file in the same instrument folder. You will access and control this small GUI totally by your NewInstrument class. 

Below shows a minimum example (newInstrument.py):

    from logging_setup import getLogger #General Class for all scripts logging in the same file
    logger = getLogger()

    from dataHandler import DataHandler, FinalMeta

    class NewInstrument(QtWidgets.QWidget, DataHandler, metaclass=FinalMeta):
        def __init__(self, parent=None):
            super().__init__(parent)
            loadUi("instruments\myNewInstrumetLayout.ui", self) #import the designer .ui file (all the widget classes are imported whith the names defined in QtDesigner)
            logger.info("New Instrument Started")


Once you have created a new instrument class and saved it into a new file in the instruments folder, along with its .ui file, you need to tell the NanoScanner to consider it. It is done by importing in instruments.py file your class and adding it to the scanModes dictionary. Example

    import hyperspectral
    import counter
    import newInstrument

    scanModes = {
        "Hyperspectral": hyperspectral.Hyperspectral(),
        "Counter": counter.Counter()
        "NewInstrument": newInstrument.NewInstrument()
    }

All available peripherals will be displayed on the main screen as Tabs. Once a peripheral (Tab) is selected, the specific configurations you programmed are shown and can be set. The scan will be performed in that chosen mode. To correctly provide the scan data, there are some abstract functions in the DataHandler class which also have to be implemented in your NewInstrument class:

    def setDataParams(self, Xdim, Ydim):
    """ Creates the data set for a scan, Xdim and Ydim represent the scan matrix dimensions. For example, hyperspectral scanning uses a (Xdim, Ydim, (x_data,y_data)) numpy array. Each pixel represents a spectrum"""
    
    def getDataDuringScan(self, indexPos):
    """ Returns the data to be shown during the scan.  You have to return an image data and a plot data in this order. 
    Image data structure is a multidimensional (Xdim, Ydim) numpy array with floats eg. np.ones((Xdim,Ydim)). 
    Plot data sctructure is a (X_data, Y_data) floats """
    
    def getCurveData(self, indexPos):
    """ If there is a plot data for each pixel (indexPos representing the index position), return the plot data numpy-array with this method. If it is not the case, return None """
    
    def getRawData(self):
    """ Returns the numpy data structure to be saved """
    
    def close(self):
    """ Close the communication with the instruments securetely """
    
### Plots
Image Plot and CurvePlot shows the color map and the line plot, respectively, emitted by ''getDataDuringScan''.
The plots are interactive, which means that one can zoom in, zoom out, apply filters and others. Also, one can export directly the plotted data as a .npy file (numpy file - open it using python library) or even the shown image as a .png.

### Dialogs
#### Piezo Dialog
Controls the piezo parameters, which will be used to drive voltage to the piezo. Several piezo systems with different parameters can be implemented. All the information will be saved into a .plk file. Once you start the program, you can select your predefined system. Caution must be taken here, since driving voltages out of the piezo's specification can cause permanent damage to the device. In addition, high voltage rates also can damage the equipment.

### Scanning
Once 'Start Scan' pushButton is pressed, most of the functionalities of the user interface are blocked and the scan acquisions start. One can intantaneously stop the scan by clicking in 'Abort Scan'.

### Saving and Exporting
The raw data, as a numpy file '.npy', can be exported to a selected folder. The checkbox mark the desired export options. Also the .png images can be exported, either directly by clicking in the right mouse button inside the plot, or by selecting the corresponding option in the checkbox.

## Credits
This software was developed by Allison Pessoa for the Nano-Optics Laboratory in Federal University of Pernambuco, Recife-PE, Brazil,
Contact: allison.pessoa@upfe.br | allisonpessoa@hotmail.com
