from pyqtgraph import PlotWidget
from pyqtgraph.opengl import GLViewWidget, GLGridItem, GLLinePlotItem, GLMeshItem
from pyqtgraph.opengl.MeshData import MeshData
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal
from sensor.socketHandler import shared_data
import numpy as np
import pyqtgraph as pg

class AccessDataThread(QThread):
    data_accessed = pyqtSignal(float)
    
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.access_interval = 1 / 100
    
    def run(self):
        while True:
            self.data_accessed.emit(self.shared_data['value'])
            self.msleep(int(self.access_interval * 1000))

class Graph(QWidget):
    accuracy_accessed = pyqtSignal(float)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._plot = PlotWidget()

        layout = QGridLayout(self)
        layout.addWidget(self._plot)

        self._plot.showGrid(x=True, y=True)
        self._plot.setLabel('left', 'Angle', units='degrees')
        self._plot.setLabel('bottom', 'Time', units='s')
        self._plot.setYRange(0, 180)

        #Initialize graph to be 0
        self._angleData = np.array([])
        self._time = np.array([])
        self._count = 0

        self._plot.plot(self._angleData, pen=(0, 229, 255))
        
        # Create timer to update plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        #Create timer to update accuracy
        self.timer2 = QtCore.QTimer()
        
    def update(self):
        if (len(self._angleData) > 20 and not self.timer2.isActive()):
            self.timer2.timeout.connect(self.calculate_accuracy)
            self.timer2.start(2000)
            print("start")

        if (self._angleData.size >= 100 and self._time.size >= 100):
            # self._angleData = np.roll(self._angleData, -1)
            # self._angleData = self._angleData[1:]
            # self._time = np.roll(self._time, -1)
            # self._time = self._time[1:]
            # self._plot.setYRange(0, 180)
            self._plot.setXRange(self._count - 10, self._count)

        self._count += 0.1
        self._angleData = np.append(self._angleData, shared_data['value'] * 100)
        self._time = np.append(self._time, self._count)

        self._idealY = np.sin(self._time) * 45 + 45
        self._plot.plot(self._time, self._angleData, pen=(0, 229, 255))
        self._plot.plot(self._time, self._idealY, pen=(0, 255, 0))
    
    def calculate_accuracy(self):
        max_difference = 180
        n = 20
        total_score = 0
        angle_data = self._angleData[-n:]
        ideal_data = self._idealY[-n:]

        for i in range(n):
            diff = abs(angle_data[i] - ideal_data[i])
            score = 1 - (diff / max_difference)
            total_score += score
        
        self.accuracy = round((total_score / n) * 100,2)
        self.accuracy_accessed.emit(self.accuracy)
        print(self.accuracy)

class threeDGraph(GLViewWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Add a grid to the 3D view
        grid = GLGridItem()
        self.addItem(grid)
        
         # Create stick man body parts
        head = self.create_head()
        body = self.create_body()
        left_arm = self.create_left_arm()
        right_arm = self.create_right_arm()
        left_leg = self.create_left_leg()
        right_leg = self.create_right_leg()

        # Add stick man body parts to the 3D view
        self.addItem(head)
        self.addItem(body)
        self.addItem(left_arm)
        self.addItem(right_arm)
        self.addItem(left_leg)
        self.addItem(right_leg)

        #Adjust camera angles
        self.setCameraPosition(distance=20, elevation=20, azimuth=-60)

    def create_head(self):
        # Define head as a sphere
        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.75)
        sphere_meshitem = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        sphere_meshitem.translate(0, 0, 5)
        
        return sphere_meshitem

    def create_body(self):
        # Define the body line data
        x = np.array([0, 0])
        y = np.array([0, 0])
        z = np.array([1, 5])

        # Create a GLLinePlotItem for the body
        body = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=2, antialias=True, mode='lines')

        return body

    def create_left_arm(self):
        # Define the left arm line data
        x = np.array([0, -1])
        y = np.array([0, 0])
        z = np.array([3, 4])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.25)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.5, 0, 3.5)
        self.addItem(joint)

        # Create a GLLinePlotItem for the left arm
        left_arm = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=2, antialias=True, mode='lines')

        return left_arm

    def create_right_arm(self):
        # Define the right arm line data
        x = np.array([0, 1])
        y = np.array([0, 0])
        z = np.array([3, 4])

        # Create a GLLinePlotItem for the right arm
        right_arm = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=2, antialias=True, mode='lines')

        return right_arm

    def create_left_leg(self):
        # Define the left leg line data
        x = np.array([0, -1])
        y = np.array([0, 0])
        z = np.array([1, 0])

        # Create a GLLinePlotItem for the left leg
        left_leg = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=2, antialias=True, mode='lines')

        return left_leg
    
    def create_right_leg(self):
        # Define the right leg line data
        x = np.array([0, 1])
        y = np.array([0, 0])
        z = np.array([1, 0])

        # Create a GLLinePlotItem for the right leg
        right_leg = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=2, antialias=True, mode='lines')

        return right_leg