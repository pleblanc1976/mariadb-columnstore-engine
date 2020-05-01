from array import array
from threading import Lock

# for tracking the history of heartbeat responses

class InvalidNode:
    pass

class HBHistory:

    # a list of a heartbeats for each node.  index = str, value = array of int,
    nodeHistory = {}

    # consts to denote state of the responses
    NoResponse = 1
    GoodResponse = 2
    LateResponse = -1
    NewNode = 0

    currentTick = 0
    tickWindow = 0
    lateWindow = 0

    mutex = Lock()

    # By default, keep a 600 heartbeat history for each node (10 mins @ 1hb/s)
    # and consider a response late if it arrives 3+ ticks late.  3 is an arbitrary small value.
    def __init__(self, tickWindow = 600, lateWindow = 3):
        self.tickWindow = tickWindow
        self.lateWindow = lateWindow

    # to simplify the logic
    def _initNode(self, node):
        self.nodeHistory[node] = array('b', [ self.GoodResponse for _ in range(self.tickWindow) ])

    def removeNode(self, node):
        self.mutex.acquire()
        if node in self.nodeHistory:
            del self.nodeHistory[node]
        self.mutex.release()

    def setCurrentTick(self, tick):
        self.mutex.acquire()

        self.currentTick = tick
        for pongs in self.nodeHistory.values():
            pongs[tick % self.tickWindow] = self.NoResponse

        self.mutex.release()

    def gotHeartbeat(self, node, tickID):
        if tickID <= self.currentTick - self.lateWindow:
            status = self.LateResponse
        else:
            status = self.GoodResponse

        self.mutex.acquire()
        if node not in self.nodeHistory:
            self._initNode(node)
        self.nodeHistory[node][tickID % self.tickWindow] = status
        self.mutex.release()

    def getNodeHistory(self, node, tickInterval):
        self.mutex.acquire()
        if node not in self.nodeHistory:
            _initNode(node)
 
        # We don't want to return values in the range where we are likely to be
        # gathering responses.
        # The return value is the range of heartbeat responses from node from
        #    tickInterval + lateWindow ticks ago to lateWindow ticks ago

        lastIndex = (self.currentTick - self.lateWindow) % self.tickWindow
        firstIndex = lastIndex - tickInterval
        history = self.nodeHistory[node]
        if firstIndex < 0:
            ret = history[firstIndex:]
            ret.extend(history[:lastIndex])
        else:
            ret = history[firstIndex:lastIndex]

        self.mutex.release()
        return ret

