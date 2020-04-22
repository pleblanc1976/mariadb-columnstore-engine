from config import Config
from socket import *
import threading
import logging
import time

class HeartBeater:
    port = 9051
    recvsock = None
    sendsock = None
    responseThread = None
    die = False
    logger = logging.getLogger(__name__)

    dieMsg = bytes(b'die')
    areYouThereMsg = bytes(b'123')
    yesIAmMsg = bytes(b'456')

    def __init__(self):
        self.recvsock = socket(type = SOCK_DGRAM)
        self.recvsock.bind(('localhost', self.port))
        self.sendsock = socket(type = SOCK_DGRAM)
        self.responseThread = threading.Thread(target = self.listenAndRespond)
        self.responseThread.start()

    def stop(self):
        self.die = True
        # break out of the recv loop
        sock = socket(type = SOCK_DGRAM)
        sock.sendto(self.dieMsg, ('localhost', self.port))
        print("stop()!")

    def listenAndRespond(self):
        while not self.die:
            try:
                # for now, all msgs are 3 bytes, so we only want to recv 3 bytes at a time in case
                # they are backed up in a recv buffer.  If msgs need to get more complex we'll need 
                # to add add'l intelligence to this.
                (data, remote) =  self.recvsock.recvfrom(3)   
                print("recv'd a msg length = {}".format(len(data)))
                if data == self.areYouThereMsg:
                    print("I acknowledge the are-you-there msg")
                    self.recvsock.sendto(self.yesIAmMsg, remote)
                elif data == self.yesIAmMsg:
                    print("Heartbeater would add to the heartbeat history here")
                elif data == self.dieMsg:
                    print("Got the die msg")
                else:
                    print("Got an unknown message: {}".format(list(data)))

            except Exception as e:
                self.logger.warning("listenAndRespond(): caught an exception: {}".format(e))
                print("listenAndRespond(): caught an exception: {}".format(e))
                time.sleep(5)

        print("listenAndRespond exiting")



