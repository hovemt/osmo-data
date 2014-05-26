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
import ConvertData


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
        filenames, _ = QtGui.QFileDialog.getOpenFileNames(
                        dir=userdir, filter="CSV Files (*.csv)")
        fileselect = FileSelectWidget(self)
        self.setCentralWidget(fileselect)


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

class FileSelectWidget(QtGui.QWidget): #pylint: disable-msg=R0904
    global filenames

    def __init__(self, parent=None):
        super(FileSelectWidget, self).__init__()

        convertbutton = QtGui.QPushButton('convert')
        convertbutton.clicked.connect(convert)
        
        self.buttons = []        
        
        self.headerlines = QtGui.QHBoxLayout()
        self.headerlines.addWidget(QtGui.QLabel("Exclude?"))
        self.headerlines.addWidget(QtGui.QLabel("Filename"))          
        
        self.filebox = QtGui.QVBoxLayout()
        self.filebox.addLayout(self.headerlines)

        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addLayout(self.filebox)

        self.hbox2 = QtGui.QHBoxLayout()
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(convertbutton)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hbox2)
        
        for i in filenames:
            self.AddWidget(i)
        
        
        
        self.setLayout(self.vbox)
        
    def AddWidget(self,filename):
        checkbox = QtGui.QCheckBox()
        self.buttons.append(checkbox)
        lineedit = QtGui.QLineEdit(QtCore.QFileInfo(filename).baseName())
        
        line = QtGui.QHBoxLayout()
        line.addWidget(checkbox)
        line.addWidget(lineedit)
        
        self.filebox.addLayout(line)

def convert():
    global filenames
    global permance
    global ex
    for file in filenames:
        permeance.append(ConvertData.det_average(file))
    savefile, _ = QtGui.QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
    df = pd.DataFrame(permeance,
                      columns=['D_k', 'Gas', 'Permeance']).sort('D_k')
    df.to_csv(savefile, index=False, sep=";")
    mainmenu = MainWidget()
    ex.setCentralWidget(mainmenu)

def main():
    global ex
    app = QtGui.QApplication(sys.argv)
    ex = OsmoData()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
