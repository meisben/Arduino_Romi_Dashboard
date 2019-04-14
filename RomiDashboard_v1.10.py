"""
Author: Ben Money-Coomes

Purpose: Test out embedding pyqtgraph into pyqt5 gui and updating live

Version control:

v1.00 - Graph is updating from text file in root folder
v1.01 - Working on adding multiple graphs and updating from the same data source (All working fine)
v1.02 - Looking into adding docked graphs for more flexible layout (this is working - in the next version I'm cleaning extra window code into new function)
v1.03 - Graphs are all in seperate dockable window (complete)
v1.04 - working on creating correct buttons, and labels in right places (complete)
v1.05 - working on connecting and disconnecting from bluetooth with correct combo and lbl functionality (combo box working)
v1.06 - continued working on v1.05 aims (complete)
v1.07 - working on porting data receiving code into program to allow receiving data from Romi and plotting it on all graphs (I think complete - need to check on Romi)
v1.08 - working on displaying current position and heading on dashboard (complete)
v1.09 - [Checkpoint] everything working, in next version i will clean up and export to github
v1.10 - Cleaning code and exporting to github
"""

import io
from io import StringIO

import numpy as np
import pandas as pd

from PyQt5.QtWidgets import (QWidget, QMessageBox, QApplication, QPushButton, QComboBox, QLabel, QGridLayout )
from PyQt5.QtGui import QIcon

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *
import pyqtgraph as pg

import bluetooth
import sys
import time


class RomiDashboard(QWidget):
    
    def __init__(self):
        super().__init__()

        self.setGeometry(500, 300, 800, 500) # x pos, y pos, x dim, y dim
        self.setWindowTitle('ROMI Dashboard')
        self.setWindowIcon(QIcon('images\icon.png'))
        
        self.initUI()   #keeps code tidy by initalising the contents of main window in a seperate function
        
           
    def initUI(self):

        headerFont = QtGui.QFont("Times", 14, QtGui.QFont.Bold) #Create font for some large labels
        dialFont = QtGui.QFont("Times", 18, QtGui.QFont.Bold)

        self.lblBluetoothAddress = QLabel( self) #create a label
        self.lblBluetoothAddress.resize(self.lblBluetoothAddress.sizeHint())
        #self.lblBluetoothAddress.setStyleSheet("background-color: powderblue")

        lblNameRomiPoseX = QLabel('X Position (mm)', self) 
        lblNameRomiPoseY = QLabel('Y Position (mm)', self) 
        lblNameRomiPoseTheta = QLabel('Orientation (degrees)', self) 
        lblNameRomiPoseX.setFont(headerFont)
        lblNameRomiPoseY.setFont(headerFont)
        lblNameRomiPoseTheta.setFont(headerFont)

        self.lblRomiPoseX = QLabel(' ---', self) 
        self.lblRomiPoseX.setStyleSheet("background-color: lightcyan")
        self.lblRomiPoseX.setFont(dialFont)

        self.lblRomiPoseY = QLabel(' ---', self)
        self.lblRomiPoseY.setStyleSheet("background-color: lightcyan")
        self.lblRomiPoseY.setFont(dialFont)

        self.lblRomiPoseTheta = QLabel(' ---', self)
        self.lblRomiPoseTheta.setStyleSheet("background-color: lightcyan")
        self.lblRomiPoseTheta.setFont(dialFont)
        
        self.comboBluetoothName = QComboBox(self) #create a combo box
        self.comboBluetoothName.addItem("Select Bluetooth Device")
        self.comboBluetoothName.resize(self.comboBluetoothName.sizeHint())
        self.comboBluetoothName.setStyleSheet("background-color: dodgerblue")
        self.comboBluetoothName.currentIndexChanged.connect(self.comboBoxChanged)
    
        qbtnScanBluetooth = QPushButton('Scan for Bluetooth Devices', self) #create a button
        qbtnScanBluetooth.clicked.connect(self.ScanBluetoothDevices)
        qbtnScanBluetooth.resize(qbtnScanBluetooth.sizeHint())
        qbtnScanBluetooth.setStyleSheet("background-color: dodgerblue")

        self.qbtnConnectBluetooth = QPushButton('Connect to Bluetooth Device', self)
        self.qbtnConnectBluetooth.clicked.connect(self.connectBluetoothDevice)
        self.qbtnConnectBluetooth.resize(self.qbtnConnectBluetooth.sizeHint())
        self.qbtnConnectBluetooth.setStyleSheet("background-color: dodgerblue")
        self.qbtnConnectBluetooth.setEnabled(False)

        self.qbtnDisconnectBluetooth = QPushButton('Disconnect from Bluetooth Device', self)
        self.qbtnDisconnectBluetooth.clicked.connect(self.disconnectBluetoothDevice)
        self.qbtnDisconnectBluetooth.resize(self.qbtnDisconnectBluetooth.sizeHint())
        self.qbtnDisconnectBluetooth.setStyleSheet("background-color: dodgerblue")
        self.qbtnDisconnectBluetooth.setEnabled(False)
        
        self.qbtnRomiReceiveData = QPushButton('Start receiving data from ROMI', self)
        self.qbtnRomiReceiveData.clicked.connect(self.animationStart)
        self.qbtnRomiReceiveData.resize(self.qbtnRomiReceiveData.sizeHint())
        self.qbtnRomiReceiveData.setEnabled(False)

        self.qbtnRomiStopData = QPushButton('Stop Receiving Data from ROMI', self)
        self.qbtnRomiStopData.clicked.connect(self.animationStop)
        self.qbtnRomiStopData.resize(self.qbtnRomiStopData.sizeHint())
        self.qbtnRomiStopData.setEnabled(False)

        qbtnProgramInfo = QPushButton('Help', self)
        qbtnProgramInfo.clicked.connect(self.displayProgramInfo)
        qbtnProgramInfo.resize(qbtnProgramInfo.sizeHint())

        # qbtnOptionalDebug = QPushButton('Debug', self)
        # qbtnOptionalDebug.clicked.connect(self.debug)
        # qbtnOptionalDebug.resize(qbtnOptionalDebug.sizeHint())

        qbtnShowGraphs = QPushButton('Display graph dashboard', self)
        qbtnShowGraphs.clicked.connect(self.openGraphWindow)
        qbtnShowGraphs.resize(qbtnShowGraphs.sizeHint())
        qbtnShowGraphs.setStyleSheet("background-color: lightgreen")
        
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(qbtnScanBluetooth, 1, 0)
        grid.addWidget(qbtnProgramInfo, 1, 1)
        
        grid.addWidget(self.comboBluetoothName, 2, 0)
        grid.addWidget(self.lblBluetoothAddress, 2, 1)
        

        grid.addWidget(self.qbtnConnectBluetooth, 3, 0)
        grid.addWidget(self.qbtnDisconnectBluetooth, 3, 1)

        grid.addWidget(self.qbtnRomiReceiveData, 4, 0)
        grid.addWidget(self.qbtnRomiStopData, 4, 1)

        # grid.addWidget(qbtnOptionalDebug, 9, 0)
        grid.addWidget(qbtnShowGraphs, 8, 0)

        grid.addWidget(lblNameRomiPoseX,10,0)
        grid.addWidget(lblNameRomiPoseY,10,1)
        grid.addWidget(lblNameRomiPoseTheta,10,2)

        grid.addWidget(self.lblRomiPoseX, 11, 0)
        grid.addWidget(self.lblRomiPoseY, 11, 1)
        grid.addWidget(self.lblRomiPoseTheta, 11, 2)
        grid.setRowMinimumHeight(11,200)
        
        self.setLayout(grid) 

        self.show()
        
        
         
    def closeEvent(self, event):
        
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()     

    def displayProgramInfo(self):
        mssg = QMessageBox.question(self, 'Romi Dashboard Information',
            '~~Information~~\n\nThis dashboard takes a serial data written arduino in the form\n"Time(s),PositionX,PositionY,Orientation(deg)".\n\nThe dashboard displays the data in realtime.\n\nThe program saves raw data to a file named "out.csv" and saves formatted\ndata to "outformatted.csv" in the root directory.\n\nData can also be exported by right clicking on graphs\n\nTo get started:\n(1) Search for bluetooth devices\n(2) Connect\n(3) Click"start receiving data from ROMI', QMessageBox.Ok)       

    def ScanBluetoothDevices(self):

        print("performing inquiry...")

        self.nearby_devices = bluetooth.discover_devices(
                duration=8, 
                lookup_names=True, 
                flush_cache=True, 
                lookup_class=False)

        if(len(self.nearby_devices)>0):
            
            print("found %d devices" % len(self.nearby_devices))

            self.comboBluetoothName.clear()

            for addr, name in self.nearby_devices:
                try:
                    print("  %s - %s" % (addr, name))
                    self.comboBluetoothName.addItem(name)
                except UnicodeEncodeError:
                    print("  %s - %s" % (addr, name.encode('utf-8', 'replace')))

            self.qbtnConnectBluetooth.setEnabled(True)


    def comboBoxChanged(self):
        #change label text to selected bluetooth device address
        self.lblBluetoothAddress.setText(self.nearby_devices[self.comboBluetoothName.currentIndex()][0])
        
    def connectBluetoothDevice(self):
        #Create Bluetooth connection
        bd_addr = self.lblBluetoothAddress.text()
        port = 1
        self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.sock.connect((bd_addr, port))

        self.qbtnDisconnectBluetooth.setEnabled(True)
        self.qbtnConnectBluetooth.setEnabled(False)
        self.qbtnRomiReceiveData.setEnabled(True)
        
    
    def disconnectBluetoothDevice(self):
        #Close Bluetooth Connection
        self.sock.close()
        self.qbtnDisconnectBluetooth.setEnabled(False)
        self.qbtnConnectBluetooth.setEnabled(True)
        self.qbtnRomiReceiveData.setEnabled(False)

    def openGraphWindow(self):

        pg.setConfigOptions(antialias=True) #makes graphs look nice
                
        self.plotPoseTX_TY = pg.PlotWidget(title ="Plot of Romi X,Y position against time") #create the graph PlotWidgets   
        self.plotPoseXY = pg.PlotWidget(title ="Plot of spacial X,Y track", )
        self.plotPoseTTheta = pg.PlotWidget(title ="Plot of Romi orientation against time")

        self.plotPoseTX_TY.setLabel('left', "Position", units='mm') #set graph options
        self.plotPoseTX_TY.setLabel('bottom', "Time", units='s')
        l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)
        l.setParentItem(self.plotPoseTX_TY.graphicsItem())
        self.c1 = self.plotPoseTX_TY.plot([], pen=(120,105,244), name="TX curve") 
        self.c2 = self.plotPoseTX_TY.plot([], pen=(0,240,174), name="TY curve")
        l.addItem(self.c1, 'X position')
        l.addItem(self.c2, 'Y position')
        #self.plotPoseTX_TY.setYRange(0, 500, padding=None, update=True)

        self.plotPoseXY.showGrid(x=True, y=True) 
        self.plotPoseXY.setLabel('left', "Y Position", units='mm')
        self.plotPoseXY.setLabel('bottom', "X Position", units='mm')
        self.plotPoseXY.setXRange(0, 1800, padding=None, update=True)
        self.plotPoseXY.setYRange(0, 1800, padding=None, update=True)

        self.plotPoseTTheta.setLabel('left', "Theta", units='degrees')
        self.plotPoseTTheta.setLabel('bottom', "Time", units='s')
        self.plotPoseTTheta.setYRange(0, 400, padding=None, update=True)

        self.win = QtGui.QMainWindow() #create a new window
        area = DockArea()              #create a dock area for layout
        self.win.setCentralWidget(area) #associate window with the dock area
        
        d1 = Dock("Dock1", size=(550, 550), closable=True) 
        d2 = Dock("Dock2", size=(550,550), closable=True)
        d3 = Dock("Dock3", size=(550,550), closable=True)
        
        area.addDock(d1, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
        area.addDock(d2, 'right')     ## place d2 at right edge of dock area
        area.addDock(d3, 'bottom')    ## place d3 at bottom edge of d1

        d1.addWidget(self.plotPoseTX_TY)
        d2.addWidget(self.plotPoseXY)
        d3.addWidget(self.plotPoseTTheta)
        
        self.win.resize(1000,700)       #resize the window to a suitable dimension
        self.win.setWindowTitle('ROMI Graph Dashboard')
        self.win.setWindowIcon(QIcon('images\icon.png'))
        self.win.show()



    def update(self):
        
        data = self.sock.recv(4024) # receive data
        #print(data) #used for debugging only
        #print(len(data)) #used for debugging only

        if(len(data)<=200 and len(data) >= 20):
            self.input = io.BytesIO(data)
            wrapperRead = io.TextIOWrapper(self.input, encoding='utf-8')
            self.wrapperWrite.write(wrapperRead.readline())

            currentOutput = self.output.getvalue().decode("utf-8") 
            testData = StringIO(currentOutput)
            
            self.df = pd.read_csv(testData, sep=",", header = None, names = ["Time", "X", "Y", "Theta"])

            self.df.to_csv('out.csv')

            self.dfPrim = self.df.dropna()
            self.dfPrim.to_csv('outFormatted.csv')

            npdfPrim = self.dfPrim.values            

            if(len(self.dfPrim.index) >= 3):
                self.c1 = self.plotPoseTX_TY.plot(npdfPrim[:,1], pen=(120,105,244), name="TX curve")
                self.c2 = self.plotPoseTX_TY.plot(npdfPrim[:,2], pen=(0,240,174), name="TY curve")
                self.plotPoseXY.plot(npdfPrim[:,1], npdfPrim[:,2], pen=(0,240,174))
                self.plotPoseTTheta.plot(npdfPrim[:,3], pen=(73,53,244), fillLevel=0, fillBrush=(149,246,219,10))

                self.lblRomiPoseX.setText(str(self.dfPrim.X.iloc[-1]))
                self.lblRomiPoseY.setText(str(self.dfPrim.Y.iloc[-1]))
                self.lblRomiPoseTheta.setText(str(self.dfPrim.Theta.iloc[-1]))
            else:
                pass
        
        else:
            pass


    def animationStart(self):

        #Check graph window is open so that data can be written to graphs
        self.openGraphWindow()

        #Disable disconnect from bluetooth button as this will cause crash
        self.qbtnDisconnectBluetooth.setEnabled(False)

        # Initialise a write buffer
        self.output = io.BytesIO()
        self.wrapperWrite = io.TextIOWrapper(self.output, encoding='utf-8', write_through=True)

        # Initialize a read buffer
        self.input = io.BytesIO()
       
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.qbtnRomiStopData.setEnabled(True)
        self.qbtnRomiReceiveData.setEnabled(False)

    def animationStop(self):
        self.timer.stop()
        self.qbtnRomiStopData.setEnabled(False)
        self.qbtnRomiReceiveData.setEnabled(True)
        self.qbtnDisconnectBluetooth.setEnabled(True)

    def debug(self):
        self.displayProgramInfo()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # optional
    ex = RomiDashboard()
    sys.exit(app.exec_())


        