import time
from PyQt5.QtWidgets import QWidget, QProgressBar, QLabel, QFrame, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from frontend.dashboardHandler import Dashboard

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cuffcare')
        self.setFixedSize(1100, 500)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.counter = 0
        self.n = 500

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        self.timer.start(5)

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.frame = QFrame()
        self.frame.setStyleSheet('''QFrame {
            background-color: #FFFFFF;
            color: rgb(40, 40, 40);
            border-radius: 10px;
        }''')
        layout.addWidget(self.frame)

        self.labelTitle = QLabel(self.frame)
        self.labelTitle.setObjectName('LabelTitle')

        # center labels
        self.labelTitle.resize(self.width() - 10, 150)
        self.labelTitle.move(0, 40) # x, y
        self.labelTitle.setText('Cuffcare')
        self.labelTitle.setAlignment(Qt.AlignCenter)
        self.labelTitle.setStyleSheet('''#LabelTitle {
            font-size: 60px;
            color: #0077C0;
            font-weight: bold;
        }''')
        # self.labelTitle.setStyleSheet('''#LabelTitle {
        #     font-size: 60px;
        #     color: #000000;
        #     font-weight: bold;
        # }''')

        self.labelDescription = QLabel(self.frame)
        self.labelDescription.resize(self.width() - 10, 50)
        self.labelDescription.move(0, self.labelTitle.height())
        self.labelDescription.setObjectName('LabelDesc')
        self.labelDescription.setText('Placeholder text 1')
        self.labelDescription.setAlignment(Qt.AlignCenter)
        self.labelDescription.setStyleSheet('''#LabelDesc {
            font-size: 30px;
            color: #0077C0;
        }''')
        # self.labelDescription.setStyleSheet('''#LabelDesc {
        #     font-size: 30px;
        #     color: #000000;
        # }''')

        self.progressBar = QProgressBar(self.frame)
        self.progressBar.resize(self.width() - 200 - 10, 50)
        self.progressBar.move(100, self.labelDescription.y() + 130)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setFormat('%p%')
        self.progressBar.setTextVisible(True)
        self.progressBar.setRange(0, self.n)
        self.progressBar.setValue(20)
        self.progressBar.setStyleSheet('''QProgressBar {
            background-color: #B8CCE4;
            color: rgb(40, 40, 40);
            border-style: none;
            border-radius: 10px;
            text-align: center;
            font-size: 30px;
        }

        QProgressBar::chunk {
            border-radius: 10px;
            background-color: qlineargradient(spread:pad x1:0, x2:1, y1:0.511364, y2:0.523, stop:0 #0077C0, stop:1 #61A8DE);
        }''')

        self.labelLoading = QLabel(self.frame)
        self.labelLoading.resize(self.width() - 10, 50)
        self.labelLoading.move(0, self.progressBar.y() + 70)
        self.labelLoading.setObjectName('LabelLoading')
        self.labelLoading.setAlignment(Qt.AlignCenter)
        self.labelLoading.setText('Connecting to the device...')
        self.labelLoading.setStyleSheet('''#LabelLoading {
            font-size: 30px;
            color: #0077C0;
        }''')

    def loading(self):
        self.progressBar.setValue(self.counter)

        if self.counter == int(self.n * 0.5):
            self.labelDescription.setText('Placeholder text 2')
        elif self.counter >= self.n:
            self.timer.stop()
            self.close()

            time.sleep(0.5)
            self.dashboard = Dashboard()
            self.dashboard.show()

        self.counter += 1
