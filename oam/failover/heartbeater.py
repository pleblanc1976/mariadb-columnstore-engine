from config import Config
from socket import *
import threading
import logging
import time
from struct import pack, unpack

from heartbeat_history import HBHistory

class HeartBeater:
    port = 9051
    recvsock = None
    sendsock = None
    responseThread = None
    die = False
    logger = logging.getLogger(__name__)

    dieMsg = bytes(b'die!00')
    areYouThereMsg = bytes(b'AYTM')
    yesIAmMsg = bytes(b'YIAM')
    sequenceNum = 0
    config = None
    history = HBHistory()

    def __init__(self, config):
        self.config = config
        self.initSockets()
        self.responseThread = threading.Thread(target = self.listenAndRespond)
        self.responseThread.start()

    def stop(self):
        self.die = True
        # break out of the recv loop
        sock = socket(type = SOCK_DGRAM)
        sock.sendto(self.dieMsg, ('localhost', self.port))

    def initSockets(self):
        self.recvsock = socket(type = SOCK_DGRAM)
        self.recvsock.bind(('localhost', self.port))
        self.sendsock = socket(type = SOCK_DGRAM)

    def listenAndRespond(self):
        while not self.die:
            try:
                # for now, all msgs are 6 bytes, so we only want to recv 6 bytes at a time in case
                # they are backed up in a recv buffer.  If msgs need to get more complex we'll need 
                # to add add'l intelligence to this.
                (data, remote) =  self.recvsock.recvfrom(6)
                if len(data) != 6:
                    continue
                (data, seq) = unpack("4sH", data)
                if data == self.areYouThereMsg:
                    msg = pack("4sH", self.yesIAmMsg, seq)
                    self.recvsock.sendto(msg, remote)
                elif data == self.yesIAmMsg:
                    # Might need to think about all of the dns activity.  Later.
                    history.gotHeartbeat(gethostbyaddr(remote[0])[0], seq)

            except Exception as e:
                self.logger.warning("listenAndRespond(): caught an exception: {}".format(e))
                time.sleep(1)

    def sendHeartbeats(self):
        nodes = self.config.getDesiredNodes()
        try: 
            for node in nodes:
                msg = pack("4sH", self.areYouThereMsg, self.sequenceNum)
                self.sendsock.sendto(msg, (node, self.port))
        except Exception as e:
            self.logger.warning("sendHeartbeats(): caught an exception: {}".format(e))
        self.sequenceNum = (self.sequenceNum + 1) % 65535
    


