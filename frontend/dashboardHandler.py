from frontend.test_dashboard import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from frontend.graph import Graph, AccessDataThread, threeDGraph
from sensor.socketHandler import shared_data, sensor_data_thread
from frontend.calibrationHandler import Calibration
from frontend.csvHandler import CSVHandler
from utility.utility import stopBlinkingAnimation
import threading


class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        #Code to simulate sensor generating data
        sensor_thread = threading.Thread(target=sensor_data_thread, args=(shared_data,))
        sensor_thread.start()

        #Poll the socketHandler for sensor data
        self.access_data_thread = AccessDataThread(shared_data)
        self.access_data_thread.data_accessed.connect(self.update_angle)
        self.access_data_thread.data_accessed.connect(self.update_report)
        self.access_data_thread.start()

        #Initialize CSV Handler
        self.report = CSVHandler()
        self.session_loaded = False

        #Initialize the graphs
        self.create_graphs()

        #Connect the load session button 
        self.pushButton.clicked.connect(lambda: self.report.load_csv(self)) #Allows parent class to be passed through

        #Connect the buttons to the start and stop events
        self.pushButton_2.clicked.connect(self.start_graph)
        self.pushButton_3.clicked.connect(self.end_graph)

        #Connect signals from the graphs
        self.graph_d.accuracy_accessed.connect(self.update_accuracy)
    
    def create_graphs(self):
        # Create a QVBoxLayout
        self.layout_d = QVBoxLayout()
        #self.layout_v = QVBoxLayout()
        #self.layout_a = QVBoxLayout()
        self.layout_s = QVBoxLayout()

        # Create a PlotWidget
        self.graph_d = Graph()
        # self.graph_v = Graph()
        # self.graph_a = Graph()
        self.graph_s = threeDGraph()

        # Add the graph to the layout
        self.layout_d.addWidget(self.graph_d)
        # self.layout_v.addWidget(graph_v)
        # self.layout_a.addWidget(graph_a)
        self.layout_s.addWidget(self.graph_s)

        # Set the layout for the QFrame
        self.frame_6.setLayout(self.layout_d)
        # self.frame_5.setLayout(layout_v)
        # self.frame_6.setLayout(layout_a)
        self.frame_4.setLayout(self.layout_s)

    def reset_graphs(self):
        # Remove the previous graphs
        self.layout_d.removeWidget(self.graph_d)
        # self.layout_v.removeWidget(self.graph_v)
        # self.layout_a.removeWidget(self.graph_a)

        # Delete the old graph once no longer referenced and frees up memory
        self.graph_d.deleteLater()
        # self.graph_v.deleteLater()
        # self.graph_a.deleteLater()

        # Create a PlotWidget
        self.graph_d = Graph()
        # self.graph_v = Graph()
        # self.graph_a = Graph()

        # Add the graph to the layout
        self.layout_d.addWidget(self.graph_d)
        # self.layout_v.addWidget(graph_v)
        # self.layout_a.addWidget(graph_a)

    def update_angle(self, data):
        self.label_10.setText(str(data))

    def update_accuracy(self, accuracy):
        self.label_12.setText(str(accuracy))

    def update_report(self, data):
        try:
            self.report.write_data(round(self.graph_d.count,1), data)
        except:
            pass

    def update_session_data(self):
        result = self.report.read_next_line()
        if result is not None:
            self.graph_d.session_time, self.graph_d.session_angle = result
            print(result)
        else:
            self.graph_d.timer3.stop()

    def start_calibration(self):
        self.calibration = Calibration()
        self.calibration.show()
        self.calibration.calibration_done.connect(self.start_graph)

    def start_graph(self):
        if self.session_loaded:
            self.report.load_session()
            self.graph_d.timer3.start(100)
            self.graph_d.timer3.timeout.connect(self.update_session_data)
            
        elif not self.session_loaded:
            self.graph_d.timer.start(100)

            #Create new session report
            self.report.start_writing()
        else:
            pass

    
    def end_graph(self):
        if self.session_loaded:
            self.graph_d.timer3.stop()
            self.graph_d.timer2.stop()
        elif not self.session_loaded:
            self.graph_d.timer.stop()
            self.graph_d.timer2.stop()
            self.report.stop_writing()

        self.reset_graphs()
        self.update_accuracy(0)

        self.labelVersion_3.setText("Session not loaded. Click on \"Load session\" to select a previous session.")
        stopBlinkingAnimation(self.labelVersion_3)
        self.session_loaded = False
        self.pushButton_2.setText("Start")
        

