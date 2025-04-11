# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 16:28:48 2025

@author: Nano2
"""


import nidaqmx
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE, Edge, CounterFrequencyMethod
import matplotlib.pyplot as plt
with nidaqmx.Task() as task:
  #task.ai_channels.add_ai_voltage_chan("Dev1/ai0")

  #task.ci_channels.add_ci_count_edges_chan('Dev1/ctr0', initial_count=0, edge=Edge.RISING)
  task.ci_channels.add_ci_freq_chan('Dev1/ctr0', max_val=10000000.0, 
                                    meas_method=CounterFrequencyMethod.HIGH_FREQUENCY_2_COUNTERS,
                                    meas_time=0.1)
  
  task.ci_channels[0].ci_freq_term = "PFI0"

  
  task.start()

  freq = task.read(READ_ALL_AVAILABLE)

print("counts: ", freq)
  
  #plt.plot(data)
  #plt.ylabel('Amplitude')
  #plt.title('Waveform')
  #plt.show()