from pyblish import api
from openpype.pipeline.publish import ValidateContentsOrder
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
        template_data = copy.deepcopy(instance.data["anatomyData"])
        template_name = "render"
        anatomy = instance.context.data['anatomy']

        # Additional template attributes necessary to retrieve the desired path
        additional_template_attributes = [
            "originalBasename",
            "originalDirname",
            "colorspace",
            "version"
        ]
        for template_attribute in additional_template_attributes:
            template_data[template_attribute] = ""

        for key_attr, value_attr in instance.data.items():
            if key_attr in additional_template_attributes:
                template_data[key_attr] = value_attr

        # Get the render template
        template_data["family"] = 'render'
        path_template_obj = anatomy.templates_obj[template_name]["folder"]
        expected_files = instance.data['expectedFiles']
        publish_folders = []
        for expected_files_by_layer in expected_files:
            for layer_name, filepaths in expected_files_by_layer.items():
                # Increment renderlayer name in the subset
                template_data["subset"] += '_{0}'.format(layer_name)
                template_filled = path_template_obj.format_strict(template_data)
                if not os.path.exists(template_filled):
                    publish_folders.append(template_filled)

        for publish_folder in publish_folders:
            self.log.debug("publish directory: \"{}\"".format(publish_folder))
            # Force creation of the folder
            os.makedirs(publish_folder)
