from frontend.dashboard import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from frontend.graph import Graph, AccessDataThread, threeDGraph, GraphVelocity, GraphAcceleration
from sensor.socketHandler import shared_data
from frontend.calibrationHandler import Calibration
from frontend.csvHandler import CSVHandler
from utility.utility import stopBlinkingAnimation
from utility.login import *


class Dashboard(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.stackedWidget.setCurrentIndex(0)

        ##Connect signup and login buttons
        self.pushButton_4.clicked.connect(self.register)
        self.pushButton_5.clicked.connect(self.login)

        #Make window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #Connect title bar buttons to their events
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize_restore.clicked.connect(self.toggle_maximize_restore)
        self.btn_close.clicked.connect(self.close)
        self.pushButton_6.clicked.connect(self.logoff)

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

    def show_register_popup(self, input):
        msg = QMessageBox()
        msg.setWindowTitle("Cuffcare")
        if (input == 1):
            msg.setText("Duplicate username detected")
        elif(input == 2):
            msg.setText("Inappropriate Password: You must have a minimum 8 character password with an uppercase and lowercase letter, no spaces, and at least 1 digit.")
        elif(input == 3):
            msg.setText("Inappropriate Username: You must have a username with no spaces!")
        else:
            pass
        x = msg.exec_()

    def show_login_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle("Cuffcare Login")
        msg.setText("Your Username and/or Password is invalid")
        x = msg.exec_()

    def register(self):
        if (check_duplicate(self.UsernameInput.text())):
            print("Duplicate detected")
            self.show_register_popup(1)
        elif(check_new_password(self.PasswordInput.text())):
            print("Inappropriate Password")
            self.show_register_popup(2)
        elif(check_new_username(self.UsernameInput.text())):
            print("Inappropriate Username")
            self.show_register_popup(3)
        else:
            create_new_user(self.UsernameInput.text(), self.PasswordInput.text())   

    def login(self):
        user_id = login_check(self.UsernameInput.text(), self.PasswordInput.text())
        if (user_id):
            self.stackedWidget.setCurrentIndex(1)
            self.label_user_icon.setText(self.UsernameInput.text()[0])

            # Clear input fields after successful login
            self.UsernameInput.setText("")
            self.PasswordInput.setText("")
        else:
            self.show_login_popup()

    def logoff(self):
        self.stackedWidget.setCurrentIndex(0)
        self.label_user_icon.setText("G")

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
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
            #self.calibration.timer.stop()

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
        

