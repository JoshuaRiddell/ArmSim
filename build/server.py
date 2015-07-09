#   ArmSim                                                             #
#   By: Joshua Riddell                                                 #
#                                                                      #
#  Permission is hereby granted, free of charge, to any person         #
#  obtaining a copy of this software and associated documentation      #
#  files (the "Software"), to deal in the Software without             #
#  restriction, including without limitation the rights to use,        #
#  copy, modify, merge, publish, distribute, sublicense, and/or sell   #
#  copies of the Software, and to permit persons to whom the           #
#  Software is furnished to do so.                                     #
#                                                                      #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,     #
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES     #
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND            #
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR        #
#  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF      #
#  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION  #
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.     #

import socket as sk
import threading
from time import sleep
from file_io import load_servo_poi

HOST = ''
PORT = 50007

SERVOPOI = load_servo_poi('servo_poi')


class NetworkThread(threading.Thread):
    def __init__(self, parent, ID):
        super().__init__()
        self.daemon = True

        self.queue = []
        self.backup_queue = []
        self.transferring = False
        self.conn = parent.conn
        self.ID = ID
        self.exit = False

    def run(self):
        print("Send loop initiated on thread: {0}".format(self.ID))

        while True:
            if self.exit:
                break
            if self.queue == []:
                sleep(0.1)
                continue

            self.transferring = True

            for item in self.queue:
                self.conn.sendall(item.encode('utf-8'))
                self.conn.recv(1024)

            self.transferring = False
            self.queue = self.backup_queue
            self.backup_queue = []


class NetworkHandler(object):
    def __init__(self, host, port):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.sock.bind((HOST, PORT))
        self.prev_angles = [0, 0, 0, 0, 0, 0, 0, 0]
        self.is_connected = False

    def connect(self):
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        print ('Connected by', addr)
        data = self.conn.recv(1024)
        print(data.decode('utf-8'))

        self.thread = NetworkThread(self, 1)
        self.thread.start()
        self.is_connected = True

    def disconnect(self):
        self.thread.exit = True
        self.thread.join()

        self.conn.shutdown(sk.SHUT_WR)
        self.conn.close()
        self.is_connected = False

    def send(self, message):
        if self.thread.transferring:
            addition = self.thread.backup_queue
        else:
            addition = self.thread.queue

        if isinstance(message, list):
            addition += [str(x) for x in message]
        else:
            addition.append(str(message))

    def send_angles(self, angles, update_all=None):
        for i in range(len(angles)):
            angle = angles[i]
            if abs(angle - self.prev_angles[i]) < 0.5 and update_all is None:
                continue
            pois = SERVOPOI[i]
            pulse = round(pois[2] + pois[4] / 180 * angle)
            if pulse < pois[1] or pulse > pois[3]:
                continue
            pulse = str(pulse)
            pin = str(pois[0])
            self.send('s ' + pin + ' ' + pulse)
            self.prev_angles[i] = angles[i]
