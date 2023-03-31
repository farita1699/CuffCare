from frontend.test_dashboard import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from frontend.graph import Graph, AccessDataThread
from sensor.socketHandler import shared_data, sensor_data_thread
import threading


class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        #Code to simulate sensor generating data
        sensor_thread = threading.Thread(target=sensor_data_thread, args=(shared_data,))
        sensor_thread.start()

        # Create a QVBoxLayout
        layout_d = QVBoxLayout()
        #layout_v = QVBoxLayout()
        #layout_a = QVBoxLayout()

        # Create a PlotWidget (your graph)
        self.graph_d = Graph()
        # self.graph_v = Graph()
        # self.graph_a = Graph()

        # Add the graph to the layout
        layout_d.addWidget(self.graph_d)
        # layout_v.addWidget(graph_v)
        # layout_a.addWidget(graph_a)

        # Set the layout for the QFrame
        self.frame_6.setLayout(layout_d)
        # self.frame_5.setLayout(layout_v)
        # self.frame_6.setLayout(layout_a)

        #Connect the buttons to the start and stop events
        self.pushButton_2.clicked.connect(self.start_graph)
        self.pushButton_3.clicked.connect(self.end_graph)
    
    def update_angle(self, data):
        self.label_10.setText(str(data))

    def start_graph(self):
        self.graph_d.timer.start(100)
        #Poll the socketHandler for sensor data
        self.access_data_thread = AccessDataThread(shared_data)
        self.access_data_thread.data_accessed.connect(self.update_angle)
        self.access_data_thread.start()
    
    def end_graph(self):
        self.graph_d.timer.stop()
        self.access_data_thread.join()

