from pyqtgraph import PlotWidget
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

class AccessDataThread(QThread):
    data_accessed = pyqtSignal(float)
    
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.access_interval = 1 / 1
    
    def run(self):
        while True:
            self.data_accessed.emit(self.shared_data['value'])
            print("Data: ", self.shared_data['value'])
            self.msleep(int(self.access_interval * 1000))

class Graph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._plot = PlotWidget()

        layout = QGridLayout(self)
        layout.addWidget(self._plot)

        self._plot.showGrid(x=True, y=True)
        self._plot.setLabel('left', 'Angle', units='degrees')
        self._plot.setLabel('bottom', 'Time', units='s')
        self._plot.setYRange(0, 180)
        #self._plot.setXRange(0, 10)

        #Initialize graph to be 0
        self._angleData = np.array([])
        self._time = np.array([])
        self._count = 0

        # x = np.linspace(-10, 10, 1000)
        # y = np.sin(x)
        self._plot.plot(self._angleData, pen=(0, 229, 255))
        
        # Create timer to update plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        #self.timer.start(100)  # Update plot every 100 milliseconds

    def update(self):
        if (self._angleData.size >= 100 and self._time.size >= 100):
            # self._angleData = np.roll(self._angleData, -1)
            # self._angleData = self._angleData[1:]
            # self._time = np.roll(self._time, -1)
            # self._time = self._time[1:]
            # self._plot.setYRange(0, 180)
            self._plot.setXRange(self._count - 10, self._count)

        self._count += 0.1
        self._angleData = np.append(self._angleData, self._count)
        self._time = np.append(self._time, self._count)

        self._idealY = np.sin(self._time) * 45 + 45
        self._plot.plot(self._time, self._angleData, pen=(0, 229, 255))
        self._plot.plot(self._time, self._idealY, pen=(0, 255, 0))            