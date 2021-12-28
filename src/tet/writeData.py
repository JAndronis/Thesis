import pandas as pd
import numpy as np
import os
import shutil

def writeData(data, destination, name_of_file):
    df = pd.DataFrame(data = data)
    _destination = os.path.join(destination, name_of_file)
    np.savetxt(_destination, df)

def read_1D_data(destination, name_of_file):
    _destination = os.path.join(destination, name_of_file)
    data = []
    for line in open(_destination, 'r'):
        lines = [i for i in line.split()]
        data.append(float(lines[0]))
    return data