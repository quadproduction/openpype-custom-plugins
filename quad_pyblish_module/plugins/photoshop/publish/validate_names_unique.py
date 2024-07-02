import pyblish.api
from openpype.pipeline.publish import (
    ValidateContentsOrder,
    PublishXmlValidationError,
    OptionalPyblishPluginMixin
)
from openpype.hosts.photoshop import api as photoshop


class ValidateNamesUniqueRepair(pyblish.api.Action):
    """Just select the layers that are with errors"""

    label = "Select Layers"
    icon = "briefcase"
    on = "failed"

    def process(self, context, plugin):
        stub = photoshop.stub()
        stub.select_layers(layer for layer in context.data['transientData'][ValidateNamesUnique.__name__])
    
        return True


class ValidateNamesUnique(
        OptionalPyblishPluginMixin,
        pyblish.api.ContextPlugin
    ):
    """Validate if the blendMode is set properly on Layers, NORMAL, and Groups, PASSTHROUGH
    """

    label = "Validate Name Unique"
    hosts = ["photoshop"]
    order = ValidateContentsOrder
    families = ["image"]
    actions = [ValidateNamesUniqueRepair]
    optional = True
    active = True

    def process(self, context):

        if not self.is_active(context.data):
            return
        
        PASSTHROUGH = "passThrough"
        NORMAL = "normal"
        returnList = list()
        msg = ""

        stub = photoshop.stub()
        layers = stub.get_layers()
        
        layerList = [layer.name for layer in layers]
        nameDuplicate = set()
        
        self.log.debug(layerList)
        for layer in layers:
            typeStr = "Group" if layer.group else "Layer"
            if layerList.count(layer.name) > 1:
                returnList.append(layer)
                if layer.name not in nameDuplicate:
                    nameDuplicate.add(layer.name)
                    msg = "{}\n\n The name {} is not unique.".format(msg, layer.name)

            else:
                continue
        
        if returnList:
            
            if not context.data.get('transientData'):
                context.data['transientData'] = dict()

            context.data['transientData'][self.__class__.__name__] = returnList
            from pprint import pprint
            pprint("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            pprint(context.data['transientData'])
            pprint("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            raise PublishXmlValidationError(self, msg)
