from xml.dom.minidom import parse
from os.path import getmtime
import threading
import logging   # to be replaced I assume
import time

class Config:
    config_file = ""

    # params read from the config file
    desired_nodes = []
    active_nodes = []
    inactive_nodes = []
    primary_node = ""

    config_thread = threading.Thread()
    config_lock = threading.Lock()
    last_mtime = 0
    die = False
    logger = logging.getLogger(__name__)

    def __init__(self, config_file = "/etc/columnstore/Columnstore.xml"):
        self.config_file = config_file
        self.load_config()
        self.config_thread = threading.Thread(target = self.load_loop);
        self.config_thread.start()

    def getDesiredNodes(self):
        self.config_lock.acquire()
        ret = self.desired_nodes
        self.config_lock.release()
        return ret

    def getActiveNodes(self):
        self.config_lock.acquire()
        ret = self.active_nodes
        self.config_lock.release()
        return ret

    def getInactiveNodes(self):
        self.config_lock.acquire()
        ret = self.inactive_nodes
        self.config_lock.release()
        return ret
 
    def stop(self):
        self.die = True

    def __del__(self):
        self.stop()
    
    def load_loop(self):
        while not self.die:
            if self.last_mtime != getmtime(self.config_file):
                self.load_config()
            time.sleep(5)

    def load_nodes(self, dom, section):
        domtmp = dom.getElementsByTagName(section)
        if len(domtmp) != 1:
            # Change this to new-oam logging calls when possible
            self.logger.warning("The config file {} should have exactly one {} section.".format(config_file, section))
            return []
        domtmp = domtmp[0].getElementsByTagName("Node")              
        return [ node.firstChild.nodeValue for node in domtmp ]

    def load_config(self):
        self.config_lock.acquire()
        try:
            dom = parse(self.config_file)
            last_mtime = getmtime(self.config_file)
        except Exception as e:
            self.config_lock.release()
            self.logger.warning("Failed to parse config file {}; got '{}'.".format(self.config_file, e))
            return False

        desired_nodes = self.load_nodes(dom, "DesiredNodes")
        if len(desired_nodes) == 0:
            self.config_lock.release()
            return False
        active_nodes = self.load_nodes(dom, "ActiveNodes")
        inactive_nodes = self.load_nodes(dom, "InactiveNodes")
        
        domtmp = dom.getElementsByTagName("PrimaryNode")
        if len(domtmp) != 1:
            self.config_lock.release()
            self.logger.warning("Failed to read the primary node from {}.  There should be one and only one PrimaryNode listed"
                .format(self.config_file))
            return False
        primary_node = domtmp[0].nodeValue

        self.desired_nodes = desired_nodes
        self.active_nodes = active_nodes
        self.inactive_nodes = inactive_nodes
        self.primary_node = primary_node
        self.last_mtime = last_mtime
        self.config_lock.release()
        return True

