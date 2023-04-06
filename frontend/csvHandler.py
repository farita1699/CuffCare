from datetime import datetime
from PyQt5.QtWidgets import QFileDialog
from utility.utility import startBlinkingAnimation
import csv

class CSVHandler:
    def __init__(self):
        super().__init__()

        self.csv_file = None
        self.csv_writer = None
        self.csv_reader = None
        self.csv_iterator = None
        self.file_name = None
    
    def start_writing(self):
        # Open CSV file and write header
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path_name = f"sessionReports/SessionReport_{current_time}.csv"
        
        self.csv_file = open(path_name, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Time", "Angle"])

    def stop_writing(self):
        # Close CSV file
        if self.csv_file:
            self.csv_file.close()
    
    def write_data(self, time, angle):
        # Write data to CSV file
        self.csv_writer.writerow([time, angle])

    #Open the csv file
    def load_session(self):
        if self.file_name:
            self.csv_file = open(self.file_name, "r", newline="")
            self.csv_reader = csv.reader(self.csv_file)
            self.csv_iterator = iter(self.csv_reader)
            next(self.csv_iterator)  # Skip the header row

    def read_next_line(self):
        if self.csv_iterator is not None:
            try:
                row = next(self.csv_iterator)
                time_value = float(row[0])
                angle_value = float(row[1])
                return time_value, angle_value
            except StopIteration:
                # End of file reached
                return None
        else:
            return None

    #Selects the csv file from the computer
    def load_csv(self, parent): 
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.file_name, _ = QFileDialog.getOpenFileName(parent, "Open Report", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if self.file_name:
            processed_name = self.file_name.rsplit("/",1)[1]
            load_status = f"Session loaded: {processed_name}"
            parent.labelVersion_3.setText(load_status)
            startBlinkingAnimation(parent.labelVersion_3)
            parent.session_loaded = True
            parent.pushButton_2.setText("Start (session)")