#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 15:25:12 2021

@author: allison
"""
import pkg_resources

import nidaqmx
from logging_setup import getLogger
logger = getLogger()
        
class PiezoCommunication():
    """DAQ Communication"""
    def __init__(self, piezoParams):
        #Initialize the piezo settings
        self.curVoltage = {'X': 0,
                              'Y': 0}
        self.finalVoltage = {'X': 0,
                             'Y': 0}
        
        
        self.updateCalibrParams(piezoParams)
                
        self.security_file_path = pkg_resources.resource_filename('instruments.piezosystem', 'securityDAQvoltage.txt')
        self._setPrevVoltage_security()
        
        #Starting communication
        try:
            self.taskX = nidaqmx.Task()
            self.taskX.ao_channels.add_ao_voltage_chan("Dev1/ao0")
            self.taskX.start()
            
            self.taskY = nidaqmx.Task()
            self.taskY.ao_channels.add_ao_voltage_chan("Dev1/ao1")
            self.taskY.start()
            logger.info("Piezo started")
            
        except Exception:
           logger.exception("Error on starting Piezo")

    def updateCalibrParams(self, parameters):
        self.minVoltage = {'X': parameters["minDoubleSpinBox_x"],
                           'Y': parameters["minDoubleSpinBox_y"],
                           'Z': parameters["minDoubleSpinBox_z"]}
        
        self.maxVoltage = {'X': parameters["maxDoubleSpinBox_x"],
                           'Y': parameters["maxDoubleSpinBox_y"],
                           'Z': parameters["maxDoubleSpinBox_z"]}
        
        self.amplification = {'X': parameters["amplificationSpinBox_x"],
                              'Y': parameters["amplificationSpinBox_y"],
                              'Z': parameters["amplificationSpinBox_z"]}
        
        self.totalStroke = {'X': parameters["totalStrokeUmDoubleSpinBox_x"],
                            'Y': parameters["totalStrokeUmDoubleSpinBox_y"],
                            'Z': parameters["totalStrokeUmDoubleSpinBox_z"]}
            
        self.maxVoltRate = {'X': parameters["maxVoltageRateDoubleSpinBox_x"],
                            'Y': parameters["maxVoltageRateDoubleSpinBox_y"],
                            'Z': parameters["maxVoltageRateDoubleSpinBox_z"]}
        
        self.conversionFactor = {}
        for key in self.minVoltage:
            self.conversionFactor[key] = self._calcConvFactor(self.maxVoltage[key],
                                                              self.minVoltage[key],
                                                              self.totalStroke[key],
                                                              self.amplification[key])
            
    def _calcConvFactor(self, maxVoltage, minVoltage, totalStroke, amplification):
        return ((maxVoltage-minVoltage)/(totalStroke*amplification)) # volts/nanometers, before amplification
                                     
    def getVoltage(self):
        """Returns the actual voltage (float) applied to Piezo"""
        return (self.finalVoltage['X'], self.finalVoltage['Y'])

    def moveSample(self, pos, save=True):#position in nm
        targetPosX = pos['X']
        targetPosY = pos['Y']
        
        self.finalVoltage['X'] = targetPosX*self.conversionFactor['X']
        self.finalVoltage['Y'] = targetPosY*self.conversionFactor['Y']
        
        if save == True:
            self._saveCurVoltage_security()
        
        self.fadeMove(self.taskX, self.maxVoltRate['X'],
                      self.curVoltage['X'], self.finalVoltage['X']),
        
        self.fadeMove(self.taskY, self.maxVoltRate['Y'],
                      self.curVoltage['Y'], self.finalVoltage['Y'])
        
        self.curVoltage['X'] = self.finalVoltage['X']
        self.curVoltage['Y'] = self.finalVoltage['Y']
        logger.info("Drive Piezo to x: %f, y: %f", \
                    targetPosX, targetPosY)

    def _saveCurVoltage_security(self):
        """Saves the current final voltage into a file.
        This file will be opened when the program starts and the voltage recovered"""
        
        try:
            securityFile = open(self.security_file_path, 'w')
            securityFile.write(str(self.finalVoltage['X']) +","+ \
                               str(self.finalVoltage['Y']))
            securityFile.close()
            logger.info("Security Voltage set to x: %f, y: %f", \
                        self.finalVoltage['X'], \
                        self.finalVoltage['Y'])
        except Exception:
            logger.exception("Could not save the security position")

    def _setPrevVoltage_security(self):
        """Opens the security file with the finals voltages. Sets as the current voltage"""
        try:
            securityFile = open(self.security_file_path, 'r')
            voltageString = securityFile.read()
            securityFile.close()
            voltages = voltageString.split(',')
            self.finalVoltage['X'] = float(voltages[0]) 
            self.finalVoltage['Y'] = float(voltages[1]) 

        except Exception as erro:
            errorMessage =  str(erro.args[0])
            print(errorMessage)

    def fadeMove(self, task, voltageRate, curVoltage, finalVoltage):
        try:
            if finalVoltage > curVoltage:
                voltage = curVoltage
                while (voltage < finalVoltage):
                    voltage = round(voltage + 0.001*voltageRate, 4)
                    task.write(voltage, auto_start=True)
            if finalVoltage < curVoltage:
                voltage = curVoltage
                while (voltage > finalVoltage):
                    voltage = round(voltage - 0.001*voltageRate, 4)
                    task.write(voltage, auto_start=True)
            if finalVoltage == curVoltage:
                pass

        except Exception as erro:
            errorMessage =  str(erro.args[0])
            print(errorMessage)
    
    def close(self):
        self.taskX.stop()
        self.taskX.close()
        self.taskY.stop()
        self.taskY.close()
        logger.info("Piezo Closed")
        
        
if __name__ == "__main__":
    piezo = PiezoCommunication()
    #piezo.close()