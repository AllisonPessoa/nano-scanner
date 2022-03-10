# NanoScanner

##Overview

NanoScanner is an environment to perform scan imaging of micro and nanosystems. It executes sample pixel-by-pixel scan, with nanometric spatial resolution, while acquires information from any desired peripheral instrument that is interacting with the nanosystem. This brings the versatility of building images from numerous physical parameters. Applications performed with the Software includes:
* Luminescence image of single micro and nanoparticles (the detected signal is a photocounter counts)
* Hyperspectral image of single micro and nanoparticles (the detected signal is an entire spectrum by a spectrometer)
* Topography image by SPM (Scanning Probe Microscopy) setup (the detected signal is the frequency shift of the tuning fork that interacts with the sample)
* Scanning Near-field Optical Microscoy (SNOM) (the detected signal is the near-field light - by photodetectors or spectrometers, which is interacting with the scanning tip)
* Among others

NanoScanner provides the versatility of easily implementing new instruments and their controls for acquiring data, which means that NanoScanner's heart is the accurate position control in nanoscale.

## Peripherals

A piezoelectric system controls the sample position in three axis. To provide the necessary voltage to drive the piezo, this software interfaces with a Digital-to-Analog converter (DAC) (National Instruments) and the specifications can be set through a dialog.

The interface with new instruments are easily to be implemented, because all the source code is written in Python, and the peripheral programming is detached from the whole positioning control and Graphical User Interface. Once you create a new instrument, all available peripherals will be displayed on the main screen. Once a peripheral is selected, the specific configurations are shown and can be set.

## Usage

Originally, this software was developed for imaging rare-earth-doped dielectric nanoparticles interacting with light. Thus, the built-in peripherals are specific for communicating with the instruments available in our Laboratories, which are:

* **National Instruments ADC (Analog-to-Digital Converter)**: Reads the analog output from a home-assembled photon counter, which counts the number of incoming pulses from the photodetector and transforms it to a voltage level.

* **Princeton Instruments Monochomator + Andor Solis CCD camera**: This is a typical spectrometer setup for acquiring the spectrum of the particles. The monochomator is responsible for splitting the white light into the CCD camera's sensors. The internal control of both is possible with Python (See pylablib? library), but requires a thorough understanding of the instrument's internal functions and workflows for correctly operating, otherwise could damage the hardware. A more secure approach is to use the manufacture's software for taking the spectra automatically, and constantly, then saving them in a folder (this is possible with the camera's internal programming language), which the scanning routine will be constantly monitoring for new data. When the spectrum file is modified, the routine take that as a pixel's information, and move for the next.

## Installation

### Dependencies

## Documentation

### General
NanoScanner features Widgets Tool Tips, which means that when one places the mouse onto an object (e.g. Text Lines, Check Boxes, etc.), it shows a small text with important information to the correct usage of the widget.

### Positioning Control
The positioning control is responsible for moving the sample through the space. A coarse movement is adjusted by changing the scan center, while a fine movement is set either by clicking on the Image Plot, by pressing the arrow buttons on keyboard (top, bottom, left, right for 2D positioning on the same Z-plane, ~~and pgUp, pgDn for modifying the Z position~~), or by setting a value on the position SpinBox. Careful must be taken here since the center position can strike all the piezo's available displacement. The range of the fine movement and the step size are defined in the scan properties panel. There are lockers to the movement in order to keep it safe. If the 'Locker Rel Movement' checkBoxe is checked, the software will not drive voltage to the piezo, but the positioning system still works and the corresponding pixel's data are still showed.


### Peripherals Control
The scanning has the versatility of accept acquiring any type of data during scan, examples are: floats, lists, strings. However, a 2D color map (basically a matrix) must be chosen to be shown in the image plot as false colors, which can be the output of some analysis of the input data.

The peripherals are implemented as Tabs. Each tab corresponds to a peripheral with their own methods of acquiring, manipulating and exporting data. One a Tab is selected, the scan will be done with that corresponding peripheral. One can set new peripherals and/or provide new real-time data analysis by writing/modifying the peripheral scripts. There is an architecture for the instrument class. More information on append...

### Plots
Image Plot shows the color map defined by the selected peripheral. Curve Plot is showed if the data is multidimentional.
The plots are interactive, which means that one can zoom in, zoom out, apply filters and others, by using the mouse. Also, one can export directly the plotted data as a .txt file or even the shown image as a .png, though NanoScanner is provided with a file system .nsn, which saves all of the information
and can be opened later on. Other settings, like the pixel size and the plot limits are modified by changing the scan properties.

### Dialogs
#### Piezo Dialog
Controls the piezo parameters, which will be used to drive voltage to the piezo. Several piezo systems with different parameters can be implemented, and the all information will be saved into a .plk file. Once you start the program, you can select your predefined system. Caution must be taken here, since driving voltages out of the piezo's specification can cause permanently damage to the device.

### Scanning
Once Start Scan pushButton is pressed, the

### Saving and Exporting
File system.

## Credits
This software was developed by Allison Pessoa for the Nano-Optics Laboartory in Federal University of Pernambuco, Recife-PE, Brazil,
Contact: allison.pessoa@upfe.br | allisonpessoa@hotmail.com
