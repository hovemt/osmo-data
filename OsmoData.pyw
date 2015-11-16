#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
OsmoData is a tool to convert a number of files to a single csv files with
the average permeance per gas

@author: hovem
"""
import sys
from PyQt4 import QtGui
import matplotlib
## Make sure that matplotlib only uses a qt4 backend
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os.path


userdir = os.path.expanduser("~")
filenames = list()
filewidget = []

HEADERS = ['systime', 'exptime', 'status', 'A', 'B', 'F1', 'F2', 'F3',
           'F4', 'P1', 'P2', 'P3', 'C', 'T1', 'T2', 'Tband', 'Tcell',
           'Pdiff', 'Fcorr', 'Perm', 'D', 'P2hold', 'P2frac',
           'Thold', 'Fraw', 'E', 'F', 'G', 'H', 'I']

GASES = ["Helium", "Nitrogen", "Methane", "Hydrogen", "Carbon dioxide"]
SIZES = [2.6, 3.64, 3.8, 2.89, 3.3]

class OsmoData(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(OsmoData, self).__init__(parent)
        self.createToolbar()
        main_window = MainWidget(self)

        self.setGeometry(300, 300, 500, 150)
        self.setWindowTitle('OsmoData Converter')
        self.setWindowIcon(QtGui.QIcon('images/osmo.png'))
        self.setCentralWidget(main_window)
        self.show()

    def createToolbar(self):
        openAction = QtGui.QAction(QtGui.QIcon('images/document-open.png'),
                                   'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open datafiles')
        openAction.triggered.connect(self.openfile)

        exitAction = QtGui.QAction(QtGui.QIcon('images/application-exit.png'),
                                   'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        #Toolbar construction
        self.toolbar = self.addToolBar('File')
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(exitAction)

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def openfile(self):
        #Here we will open the directory with the datafiles
        fns = QtGui.QFileDialog.getOpenFileNames(
                        directory=userdir, filter="CSV Files (*.csv)")

        if not fns:
            return

        self.loadfiles(fns)


    def loadfiles(self, fns):
        global filenames

        filenames = fns
        fileselect = FileSelectWidget(self)
        self.setCentralWidget(fileselect)


class MainWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        label = QtGui.QLabel('Open a file to start the data conversion process')

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(label)
        hbox.addStretch(1)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

class FileSelectWidget(QtGui.QWidget):
    global filenames
    global filewidget

    def __init__(self, parent=None):
        super(FileSelectWidget, self).__init__()
        self.setFixedHeight(300)
        self.setMinimumWidth(500)
        convertbutton = QtGui.QPushButton('convert')
        convertbutton.clicked.connect(convert)
        widget = QtGui.QWidget()

        self.filebox = QtGui.QGridLayout()
        self.filebox.addWidget(QtGui.QLabel("Filename"),0,0)
        self.filebox.addWidget(QtGui.QLabel("Gas"),0,1)
        widget.setLayout(self.filebox)

        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(convertbutton)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(scroll)
        vbox.addStretch(1)
        vbox.addLayout(hbox2)

        for i in filenames:
            self.AddWidget(i)

        self.setLayout(vbox)

    def AddWidget(self,filename):
        """
        Adds a textbox and a dropdown for each filename. The dropdown contains
        the gas that should be passed to det_average.

        The gases are now selected based on the measurement program:
        001: heating
        002: Helium
        003: Nitrogen
        004: Methane
        005: Hydrogen
        006: Carbon dioxide

        Extra temperatures follow the same pattern, so by using a modulus we can
        extract which gas is used.

        In the future the gas should be somehow incorporated into the datafile
        """
        row = self.filebox.rowCount()

        lineedit = QtGui.QLineEdit(filename)

        gasselect = QtGui.QComboBox()
        gasselect.addItems(["---","Helium","Nitrogen","Methane","Hydrogen","Carbon dioxide"])

        gas = findGas(filename)

        if gas == '':
            #TODO: Now we check for gas based on filename, extract gas from data.
            if filename.find('__') >= 0:
                num = int(filename[filename.rfind('__')+2:filename.rfind('.')])-1
                index = num % 6
                gasselect.setCurrentIndex(index)
        else:
            gasselect.setCurrentIndex(GASES.index(gas)+1)

        filewidget.append([lineedit, gasselect])
        self.filebox.addWidget(lineedit, row, 0)
        self.filebox.addWidget(gasselect, row, 1)

def findGas(filename):
    """
    Find gas from the status message in filename. The format in
    the status comment is "Measuring - Gasname"
    """
    found = ''

    with open(filename, 'r') as inF:
        for line in inF:
            if "Measuring" in line:
                found = line
                break #Only need first occurence

    if found == '':
        return ''
    else:
        # check if there is a gas name for backwards compatibility
        comment = found.split('\t')[2].split(' ')
        if len(comment) > 1:
            return comment[2]
        else:
            return ''
    

def det_average(fname, gas):
    """"
    This function returns the average permeance for the specified filename and
    gas. It will plot the permeance versus time, after which two points must be
    selected to calculate the average between those points.

    Input: filename (str), gas (str)
    Ouput: diameter (float), gas (str), permeance (float), temp (float),
            gas flow (float), pdiff (float), tband (float)

    """
    #TODO: select gas from status
    diameter = SIZES[GASES.index(gas)]
    data = pd.read_csv(fname, delimiter='\t', header=0, names=HEADERS)
    datacrop = data[data['status'].str.startswith("Measuring")] #pylint: disable-msg=E1103
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



def convert():
    """
    Convert is called to iterate over the filenames in FileSelectWidget. For
    each filename it calls det_average with the appropiate gas.

    After the iteration it saves the array to which all data is written to a
    CSV file, which is saved on the specified place.
    """
    global filenames
    global ex
    global filewidget
    permeance = []

    for item in filewidget:
        if item[1].currentText() == '---':
            pass
        else:
            permeance.append(det_average(item[0].text(), item[1].currentText()))

    #TODO: put the results to a screen before saving.

    savefile = QtGui.QFileDialog.getSaveFileName(filter="CSV Files (*.csv)",
                                                    directory=os.path.dirname(filenames[0]))

    if not savefile:
        return

    df = pd.DataFrame(permeance,
                      columns=['D_k', 'Gas', 'Permeance (mol m-2 s-1 Pa-1)', 'Temp (C)', 'Flow (ml/min) AIR', 'Pdiff (bar)','T_band']).sort_values(['T_band','D_k'])
    df.to_csv(savefile, index=False, sep=";")
    #Change back to main window after conversion
    mainmenu = MainWidget()
    filewidget = [] # Make sure we can do a second run
    ex.setCentralWidget(mainmenu)

def main():
    global ex
    app = QtGui.QApplication(sys.argv)
    ex = OsmoData()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
