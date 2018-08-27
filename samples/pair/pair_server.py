import zmq
import random
import sys
import time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

while True:
    serverMsg = input("Send Message:")
    if serverMsg:
        socket.send_string("Server Message:{}".format(serverMsg))
    msg = socket.recv()
    print(msg)
    time.sleep(1)