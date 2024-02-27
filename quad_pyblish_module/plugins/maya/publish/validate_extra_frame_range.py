from pyblish import api
from openpype.pipeline.publish import ValidateContentsOrder


class ValidateExtraFrameRange(api.InstancePlugin):
    """Validate Extra Frame Range"""

    order = ValidateContentsOrder
    hosts = ["maya"]
    families = ["renderlayer", "renderlocal"]
    label = "Validate Extra Frame Range"
    optional = True

    def process(self, instance):
        """The aim is to exclude handles when ValidateFrameRange plugin is disabled

        :param context: The Pyblish context.
        :type context: pyblish.api.Context
        """
        publish_attributes = instance.data['publish_attributes']
        if not 'ValidateFrameRange' in publish_attributes:
            self.log.info("No ValidateFrameRange Plugin Detected")
            return

        if instance.data['publish_attributes']['ValidateFrameRange']['active']:
            self.log.info("ValidateFrameRange Plugin Activated - No action required")
            return

        self.log.info('Start Updating Frame Handles Data')
        instance.context.data["frameStartHandle"] = int(instance.context.data.get("frameStart"))
        instance.context.data["frameEndHandle"] = int(instance.context.data.get("frameEnd"))
        instance.context.data["handleStart"] = 0
        instance.context.data["handleEnd"] = 0
        self.log.info('Frame Handles Data successfully set')
