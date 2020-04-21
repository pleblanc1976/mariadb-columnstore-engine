import config

_config = config.Config("config-test.xml")
print("got desired_nodes = {}".format(_config.getDesiredNodes()))
print("got active_nodes = {}".format(_config.getActiveNodes()))
print("got inacive_nodes = {}".format(_config.getInactiveNodes()))
_config.stop()



