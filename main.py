import pandas as pd
import numpy as np
import os

from lib import ybus
from lib.dataLoading import load_data
from lib.ybus import Ybus_maker

if __name__=="__main__":
    fileName = "y_bus_test"
    sheetName_l=(["Bus INFO", "Branch", "Transformer", "GEN", "LOAD", "ShuntCapacitor"])

    grid_data = load_data(fileName, sheetName_l)

    Ymaker = Ybus_maker(busData=grid_data[0], lineData=grid_data[1], transData=grid_data[2], shuntCapData=grid_data[5])

    y_bus = Ymaker.mkYbus()



