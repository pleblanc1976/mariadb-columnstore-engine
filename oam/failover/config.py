from xml.dom.minidom import parse
from os.path import getmtime
import threading
import logging   # to be replaced I assume
import time

class Config:
    config_file = ""

    # params read from the config file
    _desired_nodes = []
    _active_nodes = []
    _inactive_nodes = []
    _primary_node = ""

    config_lock = threading.Lock()
    last_mtime = 0
    die = False
    logger = logging.getLogger(__name__)

    def __init__(self, config_file = "/etc/columnstore/Columnstore.xml"):
        self.config_file = config_file

    def getDesiredNodes(self):
        self.config_lock.acquire()
        self.check_reload()
        ret = self._desired_nodes
        self.config_lock.release()
        return ret

    def getActiveNodes(self):
        self.config_lock.acquire()
        self.check_reload()
        ret = self._active_nodes
        self.config_lock.release()
        return ret

    def getInactiveNodes(self):
        self.config_lock.acquire()
        self.check_reload()
        ret = self._inactive_nodes
        self.config_lock.release()
        return ret

    # returns a 3-element tuple describing the status of all nodes.
    # index 0 = all nodes in the cluster
    # index 1 = all active nodes
    # index 2 = all inactive nodes
    def getAllNodes(self):
        self.config_lock.acquire()
        self.check_reload()
        ret = (self._desiredNodes, self._activeNodes, self._inactiveNodes)
        self.config_lock.release()
        return ret
 
    def getPrimaryNode(self):
        self.config_lock.acquire()
        self.check_reload()
        ret = self._primary_node
        self.config_lock.release()
        return ret

    def load_nodes(self, dom, section):
        domtmp = dom.getElementsByTagName(section)
        if len(domtmp) != 1:
            # Change this to new-oam logging calls when possible
            self.logger.warning("The config file {} should have exactly one {} section.".format(config_file, section))
            return []
        domtmp = domtmp[0].getElementsByTagName("Node")              
        return [ node.firstChild.nodeValue for node in domtmp ]

    # returns True if a reload happened, False if no reload was necessary
    def check_reload(self):
        if self.last_mtime != getmtime(self.config_file):
            self.load_config()
            return True
        return False

    def load_config(self):
        try:
            dom = parse(self.config_file)
            last_mtime = getmtime(self.config_file)
        except Exception as e:
            self.logger.warning("Failed to parse config file {}; got '{}'.".format(self.config_file, e))
            return False

        desired_nodes = self.load_nodes(dom, "DesiredNodes")
        if len(desired_nodes) == 0:
            return False
        active_nodes = self.load_nodes(dom, "ActiveNodes")
        inactive_nodes = self.load_nodes(dom, "InactiveNodes")
        
        domtmp = dom.getElementsByTagName("PrimaryNode")
        if len(domtmp) != 1:
            self.logger.warning("Failed to read the primary node from {}.  There should be one and only one PrimaryNode listed"
                .format(self.config_file))
            return False
        primary_node = domtmp[0].nodeValue

        desired_nodes.sort()
        active_nodes.sort()
        inactive_nodes.sort()
        self._desired_nodes = desired_nodes
        self._active_nodes = active_nodes
        self._inactive_nodes = inactive_nodes
        self._primary_node = primary_node

        self.last_mtime = last_mtime
        return True

