from frontend.calibration import Ui_Dialog
from PyQt5 import QtWidgets
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
# from sensor.socketHandler import shared_data
import threading
import time

calibration_value = None

class Calibration(QDialog, Ui_Dialog):
    calibration_done = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        #Sets up the gif
        # self.movie = QMovie("load.gif")
        # self.movie.setScaledSize(QtCore.QSize(100, 100)) # Set the scaled size
        # self.label.setMovie(self.movie)
        # self.movie.start()

        #Exits the screen if cancel button is clicked
        self.pushButton.clicked.connect(self.accept)

        self.prev_value = -99
        self.counter = 0
        self.countdown_over = False
        self.countdown = 6

        #Sets up QTimer for checking if the user is not moving the arm
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.checkCalibration)
        self.timer.start(1000)

    def checkCalibration(self):
        # current_value = shared_data['value']
        current_value = 0 #Test variable

        if (abs(current_value - self.prev_value) <= 5 and current_value < 25):
            self.countdown -= 1
            self.label_3.setText(str(self.countdown))
        else:
            self.countdown = 6
            self.label_3.setText("")

        if self.countdown_over:
            global calibration_value
            calibration_value = current_value
            self.calibration_done.emit(calibration_value)
            self.accept()

        if (self.countdown == 0):
            self.countdown_over = True
            self.label_3.setText("Calibration Complete!")
        
        if (self.counter >= 2):
            self.prev_value = current_value
            self.counter == 0
        self.counter += 1

    def startCalibration(self):
        self.label_3.setText(str(self.countdown))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = Calibration()
    dialog.show()
    sys.exit(app.exec_())