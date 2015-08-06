# -*- coding: utf-8 -*-
"""
OsmoData is a tool to convert a number of files to a single csv files with
the average permeance per gas

@author: hovem
"""
import sys
# from PySide import QtGui
from PyQt4 import QtGui
import pandas as pd
import os.path
import ConvertData


userdir = os.path.expanduser("~")
filenames = list()
filewidget = [] 

class OsmoData(QtGui.QMainWindow): #pylint: disable-msg=R0904

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
        global filenames
        #Here we will open the directory with the datafiles
        filenames = QtGui.QFileDialog.getOpenFileNames(
                        directory=userdir, filter="CSV Files (*.csv)")
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

        #hbox = QtGui.QHBoxLayout()
        #hbox.addLayout(self.filebox)
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
        row = self.filebox.rowCount()
        
        lineedit = QtGui.QLineEdit(filename)
        
        gasselect = QtGui.QComboBox()
        gasselect.addItems(["---","Helium","Nitrogen","Methane","Hydrogen","Carbon dioxide"])
        
        #TODO: Now we check for gas based on filename, extract gas from data.
        if filename.find('__') >= 0:
            num = int(filename[filename.rfind('__')+2:filename.rfind('.')])-1
            index = num % 6
            gasselect.setCurrentIndex(index)
        
        filewidget.append([lineedit, gasselect])
        self.filebox.addWidget(lineedit, row, 0)
        self.filebox.addWidget(gasselect, row, 1)

def convert():
    global filenames
    global ex
    global filewidget
    permeance = []

    for item in filewidget:
        if item[1].currentText() == '---':
            pass
        else:
            permeance.append(ConvertData.det_average(item[0].text(), item[1].currentText()))
    

    savefile = QtGui.QFileDialog.getSaveFileName(filter="CSV Files (*.csv)",
                                                    directory=os.path.dirname(filenames[0]))
    df = pd.DataFrame(permeance,
                      columns=['D_k', 'Gas', 'Permeance (mol m-2 s-1 Pa-1)', 'Temp (C)', 'Flow (ml/min) AIR', 'Pdiff (bar)','T_band']).sort(['T_band','D_k'])
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
