# # -*- coding: utf-8 -*-
# """
# Created on Wed Dec  8 11:48:36 2021

# @author: Allison Pessoa
# """

import logging
import os

FORMAT = '%(asctime)s %(filename)s [%(process)d]: %(levelname)s:: %(message)s'
    
logfile = 'app.log'
if(os.path.isfile(logfile)):
        os.remove(logfile)

file_handler = logging.FileHandler(logfile, mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(FORMAT))
            
logger = logging.getLogger('wbs-server-log')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
    
def getLogger():
    return(logger)