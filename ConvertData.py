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
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter("ignore")

HEADERS = ['systime', 'exptime', 'status', 'A', 'B', 'F1', 'F2', 'F3',
           'F4', 'P1', 'P2', 'P3', 'C', 'T1', 'T2', 'Tband', 'Tcell',
           'Pdiff', 'Fcorr', 'Perm', 'D', 'P2hold', 'P2frac',
           'Thold', 'Fraw', 'E', 'F', 'G', 'H', 'I']

GASES = ["Helium", "Nitrogen", "Methane", "Hydrogen", "Carbon dioxide"]
SIZES = [2.6, 3.64, 3.8, 2.89, 3.3]



def det_average(fname, gas):
    """"
    This function plots permeance vs time to determine the average permeance
    """
    #TODO: select gas from status
    diameter = SIZES[GASES.index(gas)]
    data = pd.read_csv(fname, delimiter='\t', header=0, names=HEADERS)
    #TODO: do something with status, since gas will be added in future
    datacrop = data[data.status == "Measuring"] #pylint: disable-msg=E1103
    datacrop['Perm'].plot()
    values = plt.ginput(2)

    xlow = values[0][0]
    xhigh = values[1][0]
    #(xlow, ylow), (xhigh, yhigh) = values

    xlow = int(xlow.round())
    xhigh = int(xhigh.round())
    average = datacrop['Perm'].loc[xlow:xhigh].mean()
    temp = datacrop['Tcell'].loc[xlow:xhigh].mean()
    flow = datacrop['Fraw'].loc[xlow:xhigh].mean()
    pdiff = datacrop['Pdiff'].loc[xlow:xhigh].mean()
    tband = np.round(datacrop['Tband'].loc[xlow:xhigh].mean())
    plt.close()
    return diameter, gas, average*1E-9, temp, flow, pdiff, tband


if __name__ == '__main__':
    print("""This script is for the data-handling of OsmoData and cannot be
            used as a standalone script""")
