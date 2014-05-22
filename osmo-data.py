#/usr/bin/env python3
import sys
from PySide import QtCore, QtGui
import matplotlib
# Make sure that matplotlib only uses a qt4 backend
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
import matplotlib.pyplot as plt
import pandas as pd
import os.path


userdir = os.path.expanduser("~")


headers = ['systime', 'exptime', 'status', 'A', 'B', 'F1', 'F2', 'F3',
           'F4', 'P1', 'P2', 'P3', 'C', 'T1', 'T2', 'Tband', 'Tcell',
           'Pdiff', 'Fcorr', 'Perm', 'D', 'P2hold', 'P2frac',
           'Thold', 'Fraw', 'E', 'F', 'G', 'H', 'I']

permeance = []

def det_average(fname):
    dk, gas = find_gas(fname)
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


class OsmoData(QtGui.QMainWindow): #pylint: disable-msg=R0904

    def __init__(self, parent=None):
        super(OsmoData, self).__init__(parent)
        self.createToolbar()
        main_window = MainWidget(self)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('OsmoData Converter')
        self.setCentralWidget(main_window)
        self.show()

    def createToolbar(self):
        openAction = QtGui.QAction(QtGui.QIcon('images/file/fileopen.png'),
                                   'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open datafiles')
        openAction.triggered.connect(self.openfile)

        exitAction = QtGui.QAction(QtGui.QIcon('images/actions/exit.png'),
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
        global filenames
        #Here we will open the directory with the datafiles
        filenames, _ = QtGui.QFileDialog.getOpenFileNames(dir=userdir)
        fileselect = FileSelectWidget(self)
        self.setCentralWidget(fileselect)
        #self.show()

class MainWidget(QtGui.QWidget): #pylint: disable-msg=R0904
    
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
        
    def __init__(self, parent=None):
        super(FileSelectWidget, self).__init__(parent)

        label = QtGui.QLabel('\n'.join(filenames))

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(label)
        hbox.addStretch(1)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)
                
                
            

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = OsmoData()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


    
#==============================================================================
# This is the old code that was used for functionality
#    
#    app = QApplication(sys.argv)
# #TODO write gui to open files
# 
# filenames, _filter = QFileDialog.getOpenFileNames(filter="CSV Files (*.csv)")
# 
# for filename in filenames:
#        permeance.append(det_average(filename))
#     
# 
# savefile, _filter = QFileDialog.getSaveFileName(filter="XLS Files (*.xlsx)")
# df = pd.DataFrame(permeance, columns = ['D_k', 'Gas', 'Permeance']).sort('D_k')
# #df.to_csv(savefile)
# df.to_excel(savefile,index=False)
# app.exit()
#==============================================================================


