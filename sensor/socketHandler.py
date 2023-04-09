import time
import random
import socket

shared_data = {'value': 0}

#Code for simulating ESP32 sending data
def sensor_data_thread(shared_data):
    while True:
        shared_data['value'] = round(random.random() * 90,2)
        time.sleep(0.1)

# def sensor_data_thread(shared_data):
#     s = socket.socket()
#     while True:
#         try:
#             s.bind(('192.168.137.1', 80))
#             break
#         except:
#             print("Cannot connect to server, trying again in 5 seconds...")
#             time.sleep(5)

#     s.listen(0)

#     while True:
#         client, addr = s.accept()

#         while True:
#             content = client.recv(64)

#             if len(content) == 0:
#                 break
#             else:
#                 shared_data['value'] = int(content.decode("utf-8"))
#                 #print(shared_data['value'])
#             time.sleep(0.1)

#         client.close()

