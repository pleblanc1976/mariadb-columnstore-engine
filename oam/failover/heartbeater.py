from config import Config
from socket import *
import threading
import logging
import time
from struct import pack, unpack

from heartbeat_history import HBHistory

class HeartBeater:
    port = 9051
#    recvsock = None
#    sendsock = None
    sock = None
    sockMutex = None
    responseThread = None
    die = False
    logger = logging.getLogger(__name__)

    dieMsg = bytes(b'die!00')
    areYouThereMsg = bytes(b'AYTM')
    yesIAmMsg = bytes(b'YIAM')
    sequenceNum = 0
    config = None
    history = None
    ip_to_name = None

    def __init__(self, config, history):
        self.config = config
        self.history = history
        self.ip_to_name = {}
        self.sockMutex = threading.Lock()

    def start(self):
        self.initSockets()
        self.responseThread = threading.Thread(target = self.listenAndRespond)
        self.responseThread.start()

    def stop(self):
        self.die = True
        # break out of the recv loop
        sock = socket(type = SOCK_DGRAM)
        sock.sendto(self.dieMsg, ('localhost', self.port))
        time.sleep(1)
        self.sock.close()

    def initSockets(self):
        self.sock = socket(type = SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))

    def updateReverseDNSCache(self, ip):
        aliases = gethostbyaddr(ip)[1]
        allNodes = self.config.getDesiredNodes()
        for name in aliases:
            if name in allNodes:
                self.ip_to_name[ip] = name
                return
        self.ip_to_name[ip] = "unknown"

    def listenAndRespond(self):
        while not self.die:
            try:
                # for now, all msgs are 6 bytes, so we only want to recv 6 bytes at a time in case
                # they are backed up in a recv buffer.  If msgs need to get more complex we'll need 
                # to add add'l intelligence to this.
                (data, remote) =  self.sock.recvfrom(6)
                if len(data) != 6:
                    continue
                (data, seq) = unpack("4sH", data)
                if data == self.areYouThereMsg:
                    msg = pack("4sH", self.yesIAmMsg, seq)
                    self.send(msg, remote[0])    
                elif data == self.yesIAmMsg:
                    # Might need to think about all of the dns activity.
                    # Update.  id the name remote is using in desirednodes, store
                    # it in a map of ip->name and use it as a cache
                    if remote[0] not in self.ip_to_name:
                        self.updateReverseDNSCache(remote[0])
                    self.history.gotHeartbeat(self.ip_to_name[remote[0]], seq)

            except Exception as e:
                self.logger.warning("listenAndRespond(): caught an exception: {}".format(e))
                time.sleep(1)

    def send(self, msg, destaddr):
        self.sockMutex.acquire()
        try:
            self.sock.sendto(msg, (destaddr, self.port))
        except Exception as e:
            self.logger.warning("Heartbeater.send(): caught {}".format(e))
        finally:
            self.sockMutex.release()
        

    def sendHeartbeats(self):
        nodes = self.config.getDesiredNodes()
        msg = pack("4sH", self.areYouThereMsg, self.sequenceNum)
        self.sockMutex.acquire()
        try:
            for node in nodes:
                self.sock.sendto(msg, (node, self.port))
        except Exception as e:
            self.logger.warning("Heartbeater.sendHeartbeats(): caught an exception: {}".format(e))
        finally:
            self.sockMutex.release()
        self.sequenceNum = (self.sequenceNum + 1) % 65535
        self.history.setCurrentTick(self.sequenceNum)
    


