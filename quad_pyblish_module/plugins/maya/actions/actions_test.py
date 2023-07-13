import maya

import openpype.hosts.maya.api.plugin


class ActionTest(openpype.hosts.maya.api.plugin.ActionBase):
    families = ["model"]
    representations = ["ma", "mb"]
    hosts = ["maya"]
    label = "Action Test"
    order = 0

    def __init__(self, context, name=None, namespace=None, options=None):
        super(ActionTest, self).__init__(context, name, namespace, options)
        print("~" * 100)

    def process(self, context, name=None, namespace=None, options=None):
        print("#" * 100)
