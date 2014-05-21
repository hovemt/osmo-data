#/usr/bin/env python3
import sys
from PySide.QtGui import QApplication, QFileDialog
import matplotlib
# Make sure that matplotlib only uses a qt4 backend
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd


headers = ['systime','exptime','status','A','B','F1','F2','F3',
           'F4','P1','P2','P3','C','T1','T2','Tband','Tcell',
           'Pdiff', 'Fcorr', 'Perm','D','P2hold','P2frac',
           'Thold','Fraw','E','F','G','H','I']

permeance = []

def det_average(fname):
    dk, gas = find_gas(fname)
    data = pd.read_csv(fname,delimiter='\t', header=0, names=headers )
    datacrop = data[data.status == "Measuring"]
    datacrop['Perm'].plot()
    values = plt.ginput(2)
    (x1 , y1), (x2, y2) = values

    x1 = int(x1.round())
    x2 = int(x2.round())
    average = datacrop['Perm'].loc[x1:x2].mean()
    plt.close()
    return dk, gas, average*1E-9


#TODO create aray with filename and gas based on a selectable window
        
def find_gas(fname):
    if '__002' in fname:
        dk, gas = 2.6, 'Helium'
    elif '__003' in fname:
        dk, gas = 3.64, 'Nitrogen'
    elif '__004' in fname:
        dk, gas = 3.8, 'Methane'
    elif '__005' in fname:
        dk, gas = 2.89, 'Hydrogen'
    elif '__006' in fname:
        dk, gas = 3.3, 'Carbon dioxide'
    else:
        dk, gas = None, 'Other'
    return dk, gas
    
app = QApplication(sys.argv)
#TODO write gui to open files

filenames, _filter = QFileDialog.getOpenFileNames(filter="CSV Files (*.csv)")

for filename in filenames:
    permeance.append(det_average(filename))
    

savefile, _filter = QFileDialog.getSaveFileName(filter="XLS Files (*.xlsx)")
df = pd.DataFrame(permeance, columns = ['D_k', 'Gas', 'Permeance']).sort('D_k')
#df.to_csv(savefile)
df.to_excel(savefile,index=False)

app.exit()
