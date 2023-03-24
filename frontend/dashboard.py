from pyqtgraph import PlotWidget
from PyQt5.QtWidgets import QDesktopWidget, QGridLayout, QLabel, QMainWindow, QSizePolicy, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from frontend.graph import Graph

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dashboard')
        self.setGeometry(100, 100, 1600, 1200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QGridLayout(self.central_widget)

        # Title
        title = QLabel('Dashboard')
        title.setFont(QFont('Arial', 30))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 3)

        # Widgets
        widget1 = QLabel('Widget 1')
        widget1.setAlignment(Qt.AlignCenter)
        widget1.setStyleSheet('''QLabel {
            font-size: 24px;
            color: #0077C0;
            background-color: #FFFFFF;
            border: 1px solid #0077C0;
            border-radius: 5px;
            padding: 10px;
        }''')
        widget1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(widget1, 1, 0)

        widget2 = Graph()
        layout.addWidget(widget2, 1, 1)

        widget3 = QLabel('Widget 3')
        widget3.setAlignment(Qt.AlignCenter)
        widget3.setStyleSheet('''QLabel {
            font-size: 24px;
            color: #0077C0;
            background-color: #FFFFFF;
            border: 1px solid #0077C0;
            border-radius: 5px;
            padding: 10px;
        }''')
        widget3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(widget3, 1, 2)

        # Status bar
        self.statusBar().showMessage('Ready')

        # Center window
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        ## Create a PlotWidget object
        ## Plot data
