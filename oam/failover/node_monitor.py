from heartbeater import HeartBeater
from config import Config
from heartbeat_history import HBHistory
from agent_comm import AgentComm
import time
import threading
import logging

class NodeMonitor:

    hb = None
    hbHistory = None
    runner = None
    agent = None
    _die = False
    config = None
    samplingInterval = 0
    flakyNodeThreshold = 0    # not used yet, KI-V-SS for V1
    _inStandby = False
    _logger = None

    def __init__(agent, samplingInterval = 30, flakyNodeThreshold = 0.5):
        self.agent = agent
        self.config = Config()
        self.hbHistory = HBHistory()
        self.samplingInterval = samplingInterval
        self.flakyNodeThreshold = flakyNodeThreshold
        self._logger = logging.Logger()
        pass

    def start(self):
        self.hb = HeartBeater(self.config, self.hbHistory)
        runner = threading.Thread(target = self.monitor)
        runner.start()

    def stop(self):
        self._die = True

    def _removeRemovedNodes(self, oldNodes, newNodes):
        # if list of desired nodes shrank, remove it from heartbeat records
        diff = [ node for node in oldNodes if node not in newNodes ]
            for node in diff:
                self.hbhistory.removeNode(node)

    def _whoAmI(self):
        return socket.gethostname()

    def _pickNewActor(self, nodes):
        if self._whoAmI() == nodes[0]:
            self._isActorOfCohort = True
        else:
            self._isActorOfCohort = False
   
    def _chooseNewPrimaryNode(self, activeList, newlyDeadNodes):
        # Just going to choose the first node in the active list that
        # isn't in the newlyDeadNodes list
        for node in activeList:
            if node not in newlyDeadNodes:
                self.agentComm.designatePrimaryNode(node)

    def monitor(self):
        # This works like the main loop of a game.
        # 1) check current state
        # 2) identify the differences
        # 3) update based on the differences

        (oldDesiredNodes, oldActiveNodes, oldInactiveNodes) = self.config.getAllNodes()
        _pickNewActor(oldActiveNodes)
 
        while not self._die:
            # send heartbeats
            hb.sendHeartbeats()

            # check for config changes
            (desiredNodes, activeNodes, inactiveNodes) = self.config.getAllNodes()

            # decide if action is necessary

            # has this node been reactivated?
            if self._inStandby and self._whoAmI() in activeNodes:
                self._inStandby = False

            # has it been deactivated?
            if self._whoAmI() in inactiveNodes:
                self._inStandby = True

            # if we are in a cohort that has <= 50% of the desired nodes, enter standby
            if not self._inStandby and len(activeNodes)/len(desiredNodes) < 0.5:
                msg = "Only {} out of {} nodes are responding to pings." +
                    "  At least {} are required; entering standby mode."
                    .format(len(activeNodes), len(desiredNodes), int(desiredNodes/2) + 1)
                self.agentComm.raiseAlarm(msg)
                self._logger.severe(msg)
                self.agentComm.enterStandby()
                time.sleep(1)
                continue

            # if there was a change to the list of active nodes
            # decide if this node is the new actor in the cohort.
            if oldActiveNodes != activeNodes:
                self._pickNewActor(activeNodes)
           
            # if not the actor or this node has been disabled, nothing else for it to do
            if not self._isActorOfCohort or self._inStandby:
                time.sleep(1)
                continue
          
            # as of here, this node is the actor of a quorum
 
            # remove nodes from history
            self._removeRemovedNodes(oldDesiredNodes, newDesiredNodes)               

            # deactivate nodes that have not responded to heartbeats in reasonable time
            # V1: only remove a node that hasn't responded to any pings in the sampling period
            deactivateList = []
            for node in activeNodes:
                history = hbhistory.getNodeHistory(node, self.samplingInterval, HBHistory.GoodResponse)
                noResponses = [ x for x in history if x == HBHistory.NoResponse ]
                if len(noResponses) == self.samplingInterval:
                    deactivateList.append(node)
            # if the primary node is in this list to be deactivated, choose a new primary node.
            if self.primaryNode in deactivateList:
                self._chooseNewPrimaryNode(deactivateList)
            logg
            agentComm.deactivateNodes(deactivateList)

            # reactivate live nodes that have begun responding to heartbeats
            # V1: only reactivate a node if we have good responses for the whole sampling period
            activateList = []
            for node in inactiveNodes:
                history = hbhistory.getNodeHistory(node, self.samplingInterval, HBHistory.NoResponse)
                goodResponses = [ x for x in history if x == HBHistory.GoodResponse ]
                if len(goodResponses) == self.samplingInterval:
                    activateList.append(node)
            agentComm.activateNodes(activateList)
        
            

