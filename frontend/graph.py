from pyqtgraph import PlotWidget
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QGridLayout
import numpy as np

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
        self._plot.setXRange(0, 10)

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
        self.timer.start(100)  # Update plot every 100 milliseconds

    def update(self):
        self._count += 1
        self._angleData = np.append(self._angleData, self._count)
        self._time = np.append(self._time, self._count)
        # x = np.linspace(-10, 10, 1000)
        # y = np.sin(x)
        self._plot.plot(self._angleData, self._time, pen=(0, 229, 255))
        print("...")
            