import sys
import threading
from sensor.socketHandler import sensor_data_thread, shared_data
from PyQt5.QtWidgets import (
    QApplication
)
from frontend.splash_screen import SplashScreen
from database.db import create_database

if __name__ == "__main__":
    app = QApplication(sys.argv)

    #Initialize database
    create_database()

    #Start a separate thread to fetch sensor data
    sensor_thread = threading.Thread(target=sensor_data_thread, args=(shared_data,))
    sensor_thread.start()

    splash_screen = SplashScreen()
    splash_screen.show()

    sys.exit(app.exec())

print(sys.version)