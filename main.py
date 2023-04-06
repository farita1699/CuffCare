import sys
from PyQt5.QtWidgets import (
    QApplication
)
from frontend.splash_screen import SplashScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash_screen = SplashScreen()
    splash_screen.show()

    sys.exit(app.exec())

print(sys.version)