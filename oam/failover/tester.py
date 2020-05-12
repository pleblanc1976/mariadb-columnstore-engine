import config
import time
from socket import *
import struct


_config = config.Config("config-test.xml")
print("got desired_nodes = {}".format(_config.getDesiredNodes()))
print("got active_nodes = {}".format(_config.getActiveNodes()))
print("got inacive_nodes = {}".format(_config.getInactiveNodes()))
print("got all nodes = {}".format(_config.getAllNodes()))
print()

from heartbeater import HeartBeater
from heartbeat_history import HBHistory

hbh = HBHistory()
hb = HeartBeater(_config, hbh)
hb.start()
sock = socket(type = SOCK_DGRAM)
sock.bind(('localhost', 12345))

# Updated heartbeater to send the reply to its own port, rather than to
# the port of the sending socket.  Need to update this.
#msg = struct.pack("4sH", hb.areYouThereMsg, 1234)
#sock.sendto(msg, ('localhost', hb.port))
#print("sent the are-you-there msg")
#(data, remote) = sock.recvfrom(6)
#(data, seq) = struct.unpack("4sH", data)
#if data == hb.yesIAmMsg:
#    print("got the yes-i-am msg, seq = {}".format(seq))
#else:
#    print("got something other than the yes-i-am-msg")

hb.stop()

#from heartbeat_history import HBHistory

#hbh = HBHistory()
hbh.setCurrentTick(0)
hbh.gotHeartbeat("node1", 0)
hbh.setCurrentTick(1)
hbh.gotHeartbeat("node2", 1)
hbh.setCurrentTick(2)
hbh.setCurrentTick(10)
hbh.gotHeartbeat("node1", 9)
hbh.gotHeartbeat("node1", 2)
pongs = hbh.getNodeHistory("node1", 20)
print("Got pongs: {}".format(pongs))

# This is currently a 'manual' test, meaning the user should watch for the expected output
# In this case, because reverse dns lookup will give 'localhost', and that does not match
# node{1-3}, all nodes will appear to NodeMonitor to be offline.  Our starting condition
# is that node1 and node2 are active, and node3 is inactive.  After 30s, node1 and node2
# should be deactivated, and our DummyAgent will start printing that they are being deactivated
def testNodeMonitor1(nm):
    nm.start()
    #nm.turnOffHBResponder()
    print("Waiting for 33 secs, watch for output from DummyAgent")
    time.sleep(32)
    nm.stop()
    time.sleep(1)
    print("NodeMonitor was stopped, did it produce the right output?")

from node_monitor import NodeMonitor
nm = NodeMonitor(config = _config)
# check whether node1, node2, and node3 are in the /etc/hosts file as localhost
addr1 = gethostbyname("node1")
addr2 = gethostbyname("node2")
addr3 = gethostbyname("node3")
if addr1 == '127.0.0.1' or addr2 == '127.0.0.1' or addr3 == '127.0.0.1':
    testNodeMonitor1(nm)
else:
    print("Skipping testNodeMonitor1().  node[1-3] needs to be defined as 127.0.0.1 in /etc/hosts")









print("tester is finished")

