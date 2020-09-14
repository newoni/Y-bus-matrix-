import pandas as pd
import numpy as np
import os

'''
load_data
---------------------------------------------------------- 
|   input 
----------------------------------------------------------
fileName : str type file name,  
sheetName_l : list type excel file's sheet name list

---------------------------------------------------------- 
|   output 
----------------------------------------------------------
excel data list

----------------------------------------------------------
|   example
----------------------------------------------------------
fileName = "IEEE24BUS(수정)"
sheetName_l = ["Bus INFO", "Branch", "Transformer", "GEN", "LOAD"]

load_data(fileName, sheetName_l)
'''


def load_data(fileName, sheetName_l):
    gridData_l = []
    for sheetName in sheetName_l:
        gridData_l.append(pd.read_excel(".\\data\\"+ fileName + ".xlsx", sheetName))

    return gridData_l

