import time
import random

shared_data = {'value': None}

def sensor_data_thread(shared_data):
    while True:
        shared_data['value'] = round(random.random(),2)
        print(shared_data['value'])
        time.sleep(1)


