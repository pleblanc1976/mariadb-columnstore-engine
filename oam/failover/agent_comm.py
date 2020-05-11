# this class handles the comm with the agent; whatever it will be


# First a dummy agent
class DummyAgent:
    def __init__(self):
        pass

    def activateNodes(self, nodes):
        print("Got activateNodes({})".format(nodes))

    def deactivateNodes(self, nodes):
        print("Got deactivateNodes({})".format(nodes))

    def designatePrimaryNode(self, node):
        print("Got designatePrimaryNode({})".format(node))

    def enterStandbyMode(self):
        print("Got enterStandbyMode()")

    def getNodeHealth(self):
        print("Got getNodeHealth()")
        return 0

    def raiseAlarm(self, severity, msg):
        print("Got raiseAlarm({}, {})".format(severity, msg))


# The AgentComm class
# Doesn't do anything useful yet obviously
class AgentComm:
    
    agent = None

    def __init__(self, agent):
        if agent is None:
            self.agent = DummyAgent()
        else:
            self.agent = agent

    def activateNodes(self, nodes):
        self.agent.activateNodes(nodes)

    def deactivateNodes(self, nodes):
        self.agent.deactivateNodes(nodes)

    def designatePrimaryNode(self, node):
        self.agent.designatePrimaryNode(node)

    def enterStandbyMode(self):
        self.agent.enterStandbyMode()

    def getNodeHealth(self):
        return self.agent.getNodeHealth()

    def raiseAlarm(self, severity, msg):
        self.agent.raiseAlarm(severity, msg)


