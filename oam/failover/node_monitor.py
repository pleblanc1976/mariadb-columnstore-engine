from heartbeater import HeartBeater
from config import Config
from heartbeat_history import HBHistory
from agent_comm import AgentComm
from socket import gethostbyname_ex
import time
import threading
import logging

class NodeMonitor:

    _hb = None
    _hbHistory = None
    _agentComm = None
    _die = False
    _config = None
    samplingInterval = 0
    flakyNodeThreshold = 0    # not used yet, KI-V-SS for V1
    _inStandby = False
    _logger = None
    _testMode = False
    myName = "Knucklehead"

    def __init__(self, agent = None, config = None, samplingInterval = 30, flakyNodeThreshold = 0.5):
        self._agentComm = AgentComm(agent)
        if config is not None:
            self._config = config
        else:
            self._config = Config()
        self._hbHistory = HBHistory()
        self.samplingInterval = samplingInterval
        self.flakyNodeThreshold = flakyNodeThreshold
        self._logger = logging.Logger("NodeMonitor")
        self._whoAmI()
        print("I declare I am {}".format(self.myName))

    def start(self):
        self._hb = HeartBeater(self._config, self._hbHistory)
        self._hb.start()
        runner = threading.Thread(target = self.monitor)
        runner.start()

    def stop(self):
        self._die = True
        if not self._testMode:
            self._hb.stop()

    def _removeRemovedNodes(self, oldNodes, newNodes):
        # if list of desired nodes shrank, remove it from heartbeat records
        diff = [ node for node in oldNodes if node not in newNodes ]
        for node in diff:
            self._hbHistory.removeNode(node)

    def _whoAmI(self):
        # might have to use gethostname_ex() instead and find the name this node
        # is going by in the list
        allNodes = self._config.getDesiredNodes()
        myNames = gethostbyname_ex('localhost')[1]
        for name in myNames:
            if name in allNodes:
                self.myName = name
                return
        self.myName = gethostname()
        logger.warning("Failed to find myself in the list of desired nodes, will use {}"\
            .format(self.myName))
        return

    def _pickNewActor(self, nodes):
        if self.myName == nodes[0]:
            self._isActorOfCohort = True
        else:
            self._isActorOfCohort = False
   
    def _chooseNewPrimaryNode(self, activeList, newlyDeadNodes):
        # Just going to choose the first node in the active list that
        # isn't in the newlyDeadNodes list
        for node in activeList:
            if node not in newlyDeadNodes:
                self._agentComm.designatePrimaryNode(node)

    def monitor(self):
        # This works like the main loop of a game.
        # 1) check current state
        # 2) identify the differences
        # 3) update based on the differences

        (desiredNodes, activeNodes, inactiveNodes) = self._config.getAllNodes()
        self.primaryNode = self._config.getPrimaryNode()
        self._pickNewActor(activeNodes)
 
        while not self._die:
            # these things would normally go at the end of the loop; doing it here
            # to reduce line count & chance of missing something as we add more code
            oldDesiredNodes = desiredNodes
            oldActiveNodes = activeNodes
            oldInactiveNodes = inactiveNodes
            time.sleep(1)

            # send heartbeats
            print("NM: ping")
            self._hb.sendHeartbeats()

            # check for config changes
            (desiredNodes, activeNodes, inactiveNodes) = self._config.getAllNodes()

            # decide if action is necessary

            # has this node been reactivated?
            if self._inStandby and self.myName in activeNodes:
                self._inStandby = False

            # has it been deactivated?
            if self.myName in inactiveNodes:
                self._inStandby = True

            # if we are in a cohort that has <= 50% of the desired nodes, enter standby
            if not self._inStandby and len(activeNodes)/len(desiredNodes) <= 0.5:
                msg = "Only {} out of {} nodes are responding to pings.  At least {} are required; entering standby mode."\
                    .format(len(activeNodes), len(desiredNodes), int(len(desiredNodes)/2) + 1)
                self._agentComm.raiseAlarm(msg)
                self._logger.severe(msg)
                self._agentComm.enterStandby()
                continue

            # if there was a change to the list of active nodes
            # decide if this node is the new actor in the cohort.
            if oldActiveNodes != activeNodes:
                self._pickNewActor(activeNodes)
           
            # if not the actor or this node has been disabled, nothing else for it to do
            if not self._isActorOfCohort or self._inStandby:
                continue
          
            # as of here, this node is the actor of a quorum
 
            # remove nodes from history
            self._removeRemovedNodes(oldDesiredNodes, desiredNodes)               

            # deactivate nodes that have not responded to heartbeats in reasonable time
            # V1: only remove a node that hasn't responded to any pings in the sampling period
            deactivateList = []
            for node in activeNodes:
                history = self._hbHistory.getNodeHistory(node, self.samplingInterval, HBHistory.GoodResponse)
                noResponses = [ x for x in history if x == HBHistory.NoResponse ]
                if len(noResponses) == self.samplingInterval:
                    deactivateList.append(node)
            # if the primary node is in this list to be deactivated, choose a new primary node.
            if self.primaryNode in deactivateList:
                self._chooseNewPrimaryNode(deactivateList)
            if len(deactivateList) > 0:
                self._agentComm.deactivateNodes(deactivateList)

            # reactivate live nodes that have begun responding to heartbeats
            # V1: only reactivate a node if we have good responses for the whole sampling period
            activateList = []
            for node in inactiveNodes:
                history = self._hbHistory.getNodeHistory(node, self.samplingInterval, HBHistory.NoResponse)
                goodResponses = [ x for x in history if x == HBHistory.GoodResponse ]
                if len(goodResponses) == self.samplingInterval:
                    activateList.append(node)
            if len(activateList) > 0:
                self._agentComm.activateNodes(activateList)
        
            

