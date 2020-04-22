import config
import time
from socket import *


_config = config.Config("config-test.xml")
print("got desired_nodes = {}".format(_config.getDesiredNodes()))
print("got active_nodes = {}".format(_config.getActiveNodes()))
print("got inacive_nodes = {}".format(_config.getInactiveNodes()))
_config.stop()


from heartbeater import HeartBeater
hb = HeartBeater()
sock = socket(type = SOCK_DGRAM)
sock.sendto(hb.areYouThereMsg, ('localhost', hb.port))
print("sent the are-you-there msg")
#time.sleep(1)
hb.stop()


print("tester is finished")

