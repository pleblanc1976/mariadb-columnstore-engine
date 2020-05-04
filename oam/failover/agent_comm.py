# this class handles the comm with the agent; whatever it will be


# First a dummy agent
class Agent:
    def __init__(self):
        pass

    def activateNodes(nodes):
        pass

    def deactivateNodes(nodes):
        pass

    def designatePrimaryNode(node):
        pass

    def enterStandbyMode():
        pass

    def getNodeHealth():
        return 0

    def raiseAlarm(severity, msg):
        pass


# The AgentComm class
# Doesn't do anything useful yet obviously
class AgentComm:
    
    agent = Agent()

    def __init__(self):
        pass

    def activateNodes(nodes):
        agent.activateNodes(nodes)

    def deactivateNodes(nodes):
        agent.deactivateNodes(nodes)

    def designatePrimaryNode(node):
        agent.designatePrimaryNode(node)

    def enterStandbyMode():
        agent.enterStandbyMode()

    def getNodeHealth():
        return agent.getNodeHealth()

    def raiseAlarm(severity, msg):
        agent.raiseAlarm(severity, msg)


