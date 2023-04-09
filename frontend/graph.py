from pyqtgraph import PlotWidget
from pyqtgraph.opengl import GLViewWidget, GLGridItem, GLLinePlotItem, GLMeshItem
from pyqtgraph.opengl.MeshData import MeshData
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal
from sensor.socketHandler import shared_data
import math
import numpy as np
import pyqtgraph as pg

class AccessDataThread(QThread):
    data_accessed = pyqtSignal(float)
    
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.access_interval = 1 / 10
    
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

        #Public variables for assessing session data
        self.session_time = 0
        self.session_angle = 0

        #Initialize graph to be 0
        self._angleData = np.array([])
        self._time = np.array([])
        self.count = 0

        #Initialize calibration value
        self.calibration_value = 0

        self._plot.plot(self._angleData, pen=(0, 229, 255))
        
        #Timer to update real time plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        #Timer to update accuracy
        self.timer2 = QtCore.QTimer()

        #Timer to update session plot
        self.timer3 = QtCore.QTimer()
        self.timer3.timeout.connect(self.update_session_data)
        
    def update(self):
        if (len(self._angleData) > 20 and not self.timer2.isActive()):
            self.timer2.timeout.connect(self.calculate_accuracy)
            self.timer2.start(2000)
            print("start")

        if (self._angleData.size >= 100 and self._time.size >= 100):
            self._plot.setXRange(self.count - 10, self.count)

        self.count += 0.1
        self.calibrated_value = shared_data['value'] - self.calibration_value

        self._angleData = np.append(self._angleData, self.calibrated_value)
        self._time = np.append(self._time, self.count)

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

    def update_session_data(self):
        if (len(self._angleData) > 20 and not self.timer2.isActive()):
            self.timer2.timeout.connect(self.calculate_accuracy)
            self.timer2.start(2000)
            print("start")

        if (self._angleData.size >= 100 and self._time.size >= 100):
            self._plot.setXRange(self.session_time - 10, self.session_time)

        self._angleData = np.append(self._angleData, self.session_angle)
        self._time = np.append(self._time, self.session_time)

        self._idealY = np.sin(self._time) * 45 + 45
        self._plot.plot(self._time, self._angleData, pen=(0, 229, 255))
        self._plot.plot(self._time, self._idealY, pen=(0, 255, 0))
        
class GraphVelocity(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._plot = PlotWidget()

        layout = QGridLayout(self)
        layout.addWidget(self._plot)

        self._plot.showGrid(x=True, y=True)
        self._plot.setLabel('left', 'Angular Velocity', units='rad/s')
        self._plot.setLabel('bottom', 'Time', units='s')
        self._plot.setYRange(-20, 20)

        #Initialize graph to be 0
        self._angleData = np.array([])
        self._time = np.array([])
        self._velocityData = np.array([])
        self.count = 0

        #Initialize calibration value
        self.calibration_value = 0

        self._plot.plot(self._angleData, pen=(0, 229, 255))
        
        #Timer to update real time plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

    def update(self):
        self.count += 0.1
        self.calibrated_value = math.radians(shared_data['value'] - self.calibration_value)

        self._angleData = np.append(self._angleData, self.calibrated_value)
        self._time = np.append(self._time, self.count)

        if len(self._angleData) > 1:
            delta_angle = self._angleData[-1] - self._angleData[-2]
            time_step = self._time[-1] - self._time[-2]

            angular_velocity = delta_angle / time_step
            self._velocityData = np.append(self._velocityData, angular_velocity)

            self._plot.plot(self._time[1:], self._velocityData, pen=(0, 229, 255))

        if self._velocityData.size >= 100 and self._time.size >= 100:
            self._plot.setXRange(self.count - 10, self.count)

class GraphAcceleration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._plot = PlotWidget()

        layout = QGridLayout(self)
        layout.addWidget(self._plot)

        self._plot.showGrid(x=True, y=True)
        self._plot.setLabel('left', 'Angular Acceleration', units='rad/s^2')
        self._plot.setLabel('bottom', 'Time', units='s')
        self._plot.setYRange(-360, 360)

        # Initialize graph to be 0
        self._angleData = np.array([])
        self._velocityData = np.array([])
        self._accelData = np.array([])
        self._time = np.array([])
        self.count = 0

        # Initialize calibration value
        self.calibration_value = 0

        self._plot.plot(self._accelData, pen=(0, 229, 255))

        # Timer to update real time plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

    def update(self):
        self.count += 0.1
        self.calibrated_value = math.radians(shared_data['value'] - self.calibration_value)

        self._angleData = np.append(self._angleData, self.calibrated_value)
        self._time = np.append(self._time, self.count)

        if len(self._angleData) > 1:
            delta_angle = self._angleData[-1] - self._angleData[-2]
            time_step = self._time[-1] - self._time[-2]

            angular_velocity = delta_angle / time_step
            self._velocityData = np.append(self._velocityData, angular_velocity)

            if len(self._velocityData) > 1:
                delta_velocity = self._velocityData[-1] - self._velocityData[-2]

                angular_acceleration = delta_velocity / time_step
                self._accelData = np.append(self._accelData, angular_acceleration)

                self._plot.plot(self._time[2:], self._accelData, pen=(0, 229, 255))

        if self._accelData.size >= 100 and self._time.size >= 100:
            self._plot.setXRange(self.count - 10, self.count)



class threeDGraph(GLViewWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Add a grid to the 3D view
        grid = GLGridItem()
        self.addItem(grid)
        
        # Initialize calibrated value
        self.calibration_value = 0

        #For lateral arm raise
        self.right_arm_length = 0.35
        self.right_forearm_length = 0.5

        #Timer to update arm motion
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_arm_motion)
        self.timer.start(100)

        # Create stick man body parts
        self.head = self.create_head()
        self.neck = self.create_neck()
        self.left_shoulder = self.create_left_shoulder()
        self.right_shoulder = self.create_right_shoulder()
        self.left_arm = self.create_left_arm()
        self.right_arm = self.create_right_arm()
        self.left_forearm = self.create_left_forearm()
        self.right_forearm = self.create_right_forearm()
        self.torso = self.create_torso()
        self.left_hip = self.create_left_hip()
        self.right_hip = self.create_right_hip()
        self.left_leg = self.create_left_leg()
        self.right_leg = self.create_right_leg()
        self.left_calf = self.create_left_calf()
        self.right_calf = self.create_right_calf()
        self.left_foot = self.create_left_foot()
        self.right_foot = self.create_right_foot()



        # Add stick man body parts to the 3D view
        self.addItem(self.head)
        self.addItem(self.neck)
        self.addItem(self.left_shoulder)
        self.addItem(self.right_shoulder)
        self.addItem(self.left_arm)
        self.addItem(self.right_arm)
        self.addItem(self.left_forearm)
        self.addItem(self.right_forearm)
        self.addItem(self.torso)
        self.addItem(self.left_hip)
        self.addItem(self.right_hip)
        self.addItem(self.left_leg)
        self.addItem(self.right_leg)
        self.addItem(self.left_calf)
        self.addItem(self.right_calf)
        self.addItem(self.left_foot)
        self.addItem(self.right_foot)
        
        #Adjust camera angles
        self.setCameraPosition(distance=8, elevation=30, azimuth=135)

    def update_arm_motion(self):
        self.calibrated_value = shared_data['value'] - self.calibration_value
        self.radians = math.radians(self.calibrated_value)

        arm_location_x = self.right_arm_length * math.sin(self.radians)
        arm_location_z = 1.7-(self.right_arm_length * math.cos(self.radians))

        forearm_location_x = arm_location_x + (self.right_forearm_length * math.sin(self.radians))
        forearm_location_z = arm_location_z - (self.right_forearm_length * math.cos(self.radians))

        # Define the right arm line data
        x1 = np.array([0.25, arm_location_x])
        y1 = np.array([0, 0])
        z1 = np.array([1.7, arm_location_z])

        x2 = np.array([arm_location_x, forearm_location_x])
        y2 = np.array([0, 0])
        z2 = np.array([arm_location_z, forearm_location_z])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        self.removeItem(self.right_forearm_joint)
        self.right_forearm_joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        self.right_forearm_joint.translate(forearm_location_x, 0, forearm_location_z)
        self.addItem(self.right_forearm_joint)

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        self.removeItem(self.right_arm_joint)
        self.right_arm_joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        self.right_arm_joint.translate(arm_location_x, 0, arm_location_z)
        self.addItem(self.right_arm_joint)

        # Create a GLLinePlotItem for the right arm
        self.removeItem(self.right_arm)
        self.removeItem(self.right_forearm)
        self.right_arm = GLLinePlotItem(pos=np.vstack([x1, y1, z1]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')
        self.right_forearm = GLLinePlotItem(pos=np.vstack([x2, y2, z2]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')
        self.addItem(self.right_arm)
        self.addItem(self.right_forearm)

    def create_head(self):
        # Define head as a sphere
        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.1)
        sphere_meshitem = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        sphere_meshitem.translate(0, 0, 1.8)
        
        return sphere_meshitem

    def create_neck(self):
        x = np.array([0, 0])
        y = np.array([0, 0])
        z = np.array([1.7, 1.8])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(0, 0, 1.7)
        self.addItem(joint)

        neck = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return neck
    
    def create_left_shoulder(self):
        x = np.array([-0.25, 0])
        y = np.array([0, 0])
        z = np.array([1.7, 1.7])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.25, 0, 1.7)
        self.addItem(joint)

        left_shoulder = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_shoulder
    
    def create_right_shoulder(self):
        x = np.array([0, 0.25])
        y = np.array([0, 0])
        z = np.array([1.7, 1.7])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(0.25, 0, 1.7)
        self.addItem(joint)

        right_shoulder = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_shoulder
    
    def create_left_arm(self):
        x = np.array([-0.25, -0.25])
        y = np.array([0, 0])
        z = np.array([1.7, 1.35])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.25, 0, 1.35)
        self.addItem(joint)

        left_arm = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_arm
    
    def create_right_arm(self):
        x = np.array([0.25, 0.25])
        y = np.array([0, 0])
        z = np.array([1.7, 1.35])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        self.right_arm_joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        self.right_arm_joint.translate(0.25, 0, 1.35)
        self.addItem(self.right_arm_joint)

        right_arm = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_arm

    def create_left_forearm(self):
        x = np.array([-0.25, -0.25])
        y = np.array([0, 0])
        z = np.array([1.35, 0.85])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.25, 0, 0.85)
        self.addItem(joint)

        left_forearm = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_forearm
    
    def create_right_forearm(self):
        x = np.array([0.25, 0.25])
        y = np.array([0, 0])
        z = np.array([1.35, 0.85])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        self.right_forearm_joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        self.right_forearm_joint.translate(0.25, 0, 0.85)
        self.addItem(self.right_forearm_joint)

        right_forearm = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_forearm
    
    def create_torso(self):
        x = np.array([0, 0])
        y = np.array([0, 0])
        z = np.array([1.7, 1.1])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(0, 0, 1.1)
        self.addItem(joint)

        torso = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return torso
    
    def create_left_hip(self):
        x = np.array([-0.2, 0])
        y = np.array([0, 0])
        z = np.array([1.1, 1.1])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.2, 0, 1.1)
        self.addItem(joint)

        left_hip = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_hip
    
    def create_right_hip(self):
        x = np.array([0, 0.2])
        y = np.array([0, 0])
        z = np.array([1.1, 1.1])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.2, 0, 1.1)
        self.addItem(joint)

        right_hip = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_hip
    
    def create_left_leg(self):
        x = np.array([-0.2, -0.2])
        y = np.array([0, 0])
        z = np.array([1.1, 0.55])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.2, 0, 0.55)
        self.addItem(joint)

        left_leg = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_leg
    
    def create_right_leg(self):
        x = np.array([0.2, 0.2])
        y = np.array([0, 0])
        z = np.array([1.1, 0.55])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(0.2, 0, 0.55)
        self.addItem(joint)

        right_leg = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_leg
    
    def create_left_calf(self):
        x = np.array([-0.2, -0.2])
        y = np.array([0, 0])
        z = np.array([0.55, 0])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.2, 0, 0)
        self.addItem(joint)

        left_calf = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_calf
    
    def create_right_calf(self):
        x = np.array([0.2, 0.2])
        y = np.array([0, 0])
        z = np.array([0.55, 0])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(0.2, 0, 0)
        self.addItem(joint)

        right_calf = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_calf
    
    def create_left_foot(self):
        x = np.array([-0.2, -0.2])
        y = np.array([0, 0.1])
        z = np.array([0, 0])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(-0.2, 0.1, 0)
        self.addItem(joint)

        left_foot = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return left_foot

    def create_right_foot(self):
        x = np.array([0.2, 0.2])
        y = np.array([0, 0.1])
        z = np.array([0, 0])

        sphere_data = MeshData.sphere(rows=20, cols=20, radius=0.025)
        joint = GLMeshItem(meshdata=sphere_data, smooth=True, color=(0, 0, 1, 1))
        joint.translate(0.2, 0.1, 0)
        self.addItem(joint)

        right_foot = GLLinePlotItem(pos=np.vstack([x, y, z]).T, color=(1, 1, 0, 1), width=1, antialias=True, mode='lines')

        return right_foot