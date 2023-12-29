from pyblish import api
from openpype.pipeline.publish import ValidateContentsOrder
from openpype.pipeline.publish.lib import get_publish_template_name
import os
import copy


class ValidateRenderFolderCreation(api.InstancePlugin):
    """Validate Render Folder Creation"""

    order = ValidateContentsOrder
    hosts = ["maya"]
    families = ["renderlayer", "renderlocal"]
    label = "Validate Render Folder Creation"
    optional = True

    def process(self, instance):
        """The aim is to create the publish folder directly from the user machine and
        not from the renderfarm.

        :param context: The Pyblish context.
        :type context: pyblish.api.Context
        """
        # Get the context data
        anatomy = instance.context.data["anatomy"]
        template_data = copy.deepcopy(instance.data["anatomyData"])
        # We force the family as 'render' (Check ValidatePublishDir() Plugin)
        template_data["family"] = "render"
        # Recover the publish template
        publish_templates = anatomy.templates_obj["publish"]
        # Generate the template
        publish_folder = publish_templates["folder"].format_strict(template_data)
        publish_folder = os.path.normpath(publish_folder)

        self.log.debug("publishDir: \"{}\"".format(publish_folder))
        # Force creation of the folder
        if not os.path.exists(publish_folder):
            os.makedirs(publish_folder)
