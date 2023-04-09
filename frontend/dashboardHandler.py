from frontend.test_dashboard import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from frontend.graph import Graph, AccessDataThread, threeDGraph, GraphVelocity, GraphAcceleration
from sensor.socketHandler import shared_data
from frontend.calibrationHandler import Calibration
from frontend.csvHandler import CSVHandler
from utility.utility import stopBlinkingAnimation


class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        #Make window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #Connect title bar buttons to their events
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize_restore.clicked.connect(self.toggle_maximize_restore)
        self.btn_close.clicked.connect(self.close)

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

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize_restore.setText('Maximize')
        else:
            self.showMaximized()
            self.btn_maximize_restore.setText('Restore')
    
    def create_graphs(self):
        # Create a QVBoxLayout
        self.layout_d = QVBoxLayout()
        self.layout_v = QVBoxLayout()
        self.layout_a = QVBoxLayout()
        self.layout_s = QVBoxLayout()

        # Create a PlotWidget
        self.graph_d = Graph()
        self.graph_v = GraphVelocity()
        self.graph_a = GraphAcceleration()
        self.graph_s = threeDGraph()

        # Add the graph to the layout
        self.layout_d.addWidget(self.graph_d)
        self.layout_v.addWidget(self.graph_v)
        self.layout_a.addWidget(self.graph_a)
        self.layout_s.addWidget(self.graph_s)

        # Set the layout for the QFrame
        self.frame_6.setLayout(self.layout_d)
        self.frame_5.setLayout(self.layout_v)
        self.frame_7.setLayout(self.layout_a)
        self.frame_4.setLayout(self.layout_s)

    def reset_graphs(self):
        # Remove the previous graphs
        self.layout_d.removeWidget(self.graph_d)
        self.layout_v.removeWidget(self.graph_v)
        self.layout_a.removeWidget(self.graph_a)

        # Delete the old graph once no longer referenced and frees up memory
        self.graph_d.deleteLater()
        self.graph_v.deleteLater()
        self.graph_a.deleteLater()

        # Create a PlotWidget
        self.graph_d = Graph()
        self.graph_v = GraphVelocity()
        self.graph_a = GraphAcceleration()

        # Add the graph to the layout
        self.layout_d.addWidget(self.graph_d)
        self.layout_v.addWidget(self.graph_v)
        self.layout_a.addWidget(self.graph_a)

    def update_angle(self, data):
        self.label_10.setText(str(data-self.graph_d.calibration_value))

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

    def update_calibration_value(self, value):
        self.graph_d.calibration_value = value
        self.graph_v.calibrated_value = value
        self.graph_a.calibrated_value = value
        self.graph_s.calibration_value = value

    def start_calibration(self):
        if self.session_loaded:
            self.start_graph()
        elif not self.session_loaded:
            self.calibration = Calibration()
            self.calibration.show()
            self.calibration.calibration_done.connect(self.start_graph)
            self.calibration.calibration_done.connect(self.update_calibration_value)

    def start_graph(self):
        if self.session_loaded:
            self.report.load_session()
            self.graph_d.timer3.start(100)
            self.graph_d.timer3.timeout.connect(self.update_session_data)
            
        elif not self.session_loaded:
            self.graph_d.timer.start(100)
            self.graph_v.timer.start(100)
            self.graph_a.timer.start(100)
            self.calibration.timer.stop()

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
            self.graph_v.timer.stop()
            self.graph_a.timer.stop()
            self.report.stop_writing()

        self.reset_graphs()
        self.update_accuracy(0)

        self.labelVersion_3.setText("Session not loaded. Click on \"Load session\" to select a previous session.")
        stopBlinkingAnimation(self.labelVersion_3)
        self.session_loaded = False
        self.pushButton_2.setText("Start")
        

