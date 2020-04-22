import config
import time
from socket import *
import struct


_config = config.Config("config-test.xml")
print("got desired_nodes = {}".format(_config.getDesiredNodes()))
print("got active_nodes = {}".format(_config.getActiveNodes()))
print("got inacive_nodes = {}".format(_config.getInactiveNodes()))
print()

from heartbeater import HeartBeater
hb = HeartBeater(_config)
sock = socket(type = SOCK_DGRAM)
sock.bind(('localhost', 12345))

msg = struct.pack("4sH", hb.areYouThereMsg, 1234)
sock.sendto(msg, ('localhost', hb.port))
print("sent the are-you-there msg")
(data, remote) = sock.recvfrom(6)
(data, seq) = struct.unpack("4sH", data)
if data == hb.yesIAmMsg:
    print("got the yes-i-am msg, seq = {}".format(seq))
else:
    print("got something other than the yes-i-am-msg")

hb.stop()

print("tester is finished")

