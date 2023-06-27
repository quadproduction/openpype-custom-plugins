import copy
import pyblish.api
from openpype.lib import prepare_template_data


class CollectJsonInstances(pyblish.api.InstancePlugin):
    label = "Collect Json Instances"
    order = pyblish.api.CollectorOrder - 0.41
    hosts = ["tvpaint"]
    families = ["imagesequence"]

    def process(self, instance):
        context = instance.context
        creator_identifier = instance.data["creator_identifier"]
        self._collect_data_for_json(instance)

        subset_name = instance.data["subset"]
        instance.data["name"] = subset_name
        instance.data["label"] = "{} [{}-{}]".format(
            subset_name,
            context.data["sceneMarkIn"] + 1,
            context.data["sceneMarkOut"] + 1
        )

    def _collect_data_for_json(self, instance):
        instance.data['families'].append('imagesequence')
        creator_attributes = instance.data['creator_attributes']
        instance.data["layers"] = copy.deepcopy(
            instance.context.data['layersData']
        )
