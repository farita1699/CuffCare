import time
import random

shared_data = {'value': None}

def sensor_data_thread(shared_data):
    while True:
        shared_data['value'] = round(random.random(),2)
        time.sleep(0.1)


