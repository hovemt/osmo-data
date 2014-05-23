#/usr/bin/env python3
import sys
from PySide import QtCore, QtGui
#import matplotlib
# Make sure that matplotlib only uses a qt4 backend
#matplotlib.use('Qt4Agg')
#matplotlib.rcParams['backend.qt4'] = 'PySide'
#import matplotlib.pyplot as plt
import pandas as pd
import os.path
import convertdata


userdir = os.path.expanduser("~")
filenames = list()

permeance = list()

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
        filenames, _ = QtGui.QFileDialog.getOpenFileNames(dir=userdir,filter="CSV Files (*.csv)")
        fileselect = FileSelectWidget(self)
        self.setCentralWidget(fileselect)
        #self.show()
        
    def showMainWindow(self):
        main_window = MainWidget(self)
        self.setCentralWidget(main_window)

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
        
        convertbutton = QtGui.QPushButton('convert')
        convertbutton.clicked.connect(self.convertdata)        
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addStretch(1)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addStretch(1)        
        hbox2.addWidget(convertbutton)
        

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)
    
    def convertdata(self):
        global filenames
        global permance
        for file in filenames:
            permeance.append(convertdata.det_average(file))
        
        savefile, _ = QtGui.QFileDialog.getSaveFileName(filter="XLS Files (*.xlsx)")
        df = pd.DataFrame(permeance, columns = ['D_k', 'Gas', 'Permeance']).sort('D_k')
        df.to_excel(savefile,index=False)
       
        #TODO: give a message that it succeeded.    

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


