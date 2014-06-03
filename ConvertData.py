# -*- coding: utf-8 -*-
"""
ConvertData contains the code to convert the csv files from the Osmo
Inspector software to an average permeance

@author: hovem
"""

import matplotlib
## Make sure that matplotlib only uses a qt4 backend
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
import matplotlib.pyplot as plt
import pandas as pd
#import os.path


headers = ['systime', 'exptime', 'status', 'A', 'B', 'F1', 'F2', 'F3',
           'F4', 'P1', 'P2', 'P3', 'C', 'T1', 'T2', 'Tband', 'Tcell',
           'Pdiff', 'Fcorr', 'Perm', 'D', 'P2hold', 'P2frac',
           'Thold', 'Fraw', 'E', 'F', 'G', 'H', 'I']
           
gases = ["Helium", "Nitrogen", "Methane", "Hydrogen", "Carbon dioxide"]
dk_sizes = [2.6, 3.64, 3.8, 2.89, 3.3]           



def det_average(fname, gas):
    dk = dk_sizes[gases.index(gas)]
    data = pd.read_csv(fname, delimiter='\t', header=0, names=headers)
    datacrop = data[data.status == "Measuring"]
    datacrop['Perm'].plot()
    values = plt.ginput(2)
    (x1, y1), (x2, y2) = values

    x1 = int(x1.round())
    x2 = int(x2.round())
    average = datacrop['Perm'].loc[x1:x2].mean()
    plt.close()
    return dk, gas, average*1E-9


if __name__ == '__main__':
    print("""This script is for the data-handling of OsmoData and cannot be
            used as a standalone script""")