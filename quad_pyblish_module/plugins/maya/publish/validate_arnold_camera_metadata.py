import pyblish.api

try:
    from maya import cmds
except ImportError:
    # Ignoring, we don't want misleading error logs on jobs log on deadline.
    # Because the farm publish function imports every publish file before filtering.
    pass

from openpype.hosts.maya.api import lib
from openpype.pipeline.publish import (
    ValidateContentsOrder
)


class ValidateArnoldCameraMetadata(pyblish.api.InstancePlugin):
    """Validate Arnold Camera Metadata Render Settings"""

    order = ValidateContentsOrder
    hosts = ["maya"]
    families = ["renderlayer"]
    label = "Validate Arnold Camera Metadata"
    optional = True

    def set_metadata_attr(self, attribute, attribute_type, name, value):
        """ This make sure that no crash happens, as the script is
            launched at render time.
        """
        try:
            cmds.setAttr(
                attribute,
                "{} {} {}".format(attribute_type, name, value),
                type="string"
            )
        except Exception as e:
            print("Error occured while updating {}".format(attribute))
            print(str(e))

    def get_custom_attrs(self, nodename):
        """ get the list of custom attributes values """
        result_attr = {}
        custom_attrs = cmds.listAttr(
            "{}.customAttributes".format(nodename),
            multi=True
        )

        if not custom_attrs:
            return result_attr

        for index, attr in enumerate(custom_attrs):
            value = cmds.getAttr("{}.{}".format(nodename, attr))
            attr_values = value.split(" ")
            if len(attr_values) <= 1:
                continue
            result_attr[attr_values[1]] = {
                "type": attr_values[0],
                "index": str(index),
                "value": attr_values[2],
            }
        return result_attr

    def process(self, instance):
        """ Creates (or updates) custom metadata on the Arnold driver node.
            It gets camera information from first renderable camera of
            current active render layer.
        """
        renderable_camera = [
            cam for cam in cmds.ls(type='camera')
            if cmds.getAttr("{}.renderable".format(cam))
        ]
        if not renderable_camera:
            print("No renderable camera found!")
            return

        renderable_camera = renderable_camera[0]

        # Value is in inch, convert to mm (25.4)
        h_aperture = cmds.camera(renderable_camera, q=True, hfa=True) * 25.4
        v_aperture = cmds.camera(renderable_camera, q=True, vfa=True) * 25.4
        focus_distance = cmds.camera(renderable_camera, q=True, fd=True)
        f_stop = cmds.camera(renderable_camera, q=True, fs=True)

        # create the metadata to add
        arnold_driver = cmds.ls('defaultArnoldDriver')
        if not arnold_driver:
            print("defaultArnoldDriver not found!")
            return

        arnold_driver = arnold_driver[0]
        node_name = "{}.customAttributes".format(arnold_driver)

        new_attributes = {
            "custom/CameraApertureHorizontal": {
                "type": "FLOAT",
                "value": h_aperture,
            },
            "custom/CameraApertureVertical": {
                "type": "FLOAT",
                "value": v_aperture,
            },
            "custom/focusDistance": {
                "type": "FLOAT",
                "value": focus_distance,
            },
            "custom/fStop": {
                "type": "FLOAT",
                "value": f_stop,
            },
        }
        current_attrs = self.get_custom_attrs(arnold_driver)

        # Update existing attributes
        for attr_name, value in new_attributes.items():
            if attr_name in current_attrs.keys():
                self.set_metadata_attr(
                    "{}[{}]".format(node_name, current_attrs[attr_name]['index']),
                    value['type'],
                    attr_name,
                    value['value'],
                )
            else:
                next_index = 0
                last_index = cmds.getAttr(node_name, multiIndices=True)
                if last_index:
                    next_index = last_index[-1] + 1
                self.set_metadata_attr(
                    node_name + '[' + str(next_index) + ']',
                    value['type'],
                    attr_name,
                    value['value'],
                )

        # Add post render mel command to validate metadata
        post_mel_command = 'python("from quad_pyblish_module.plugins.maya.publish.validate_arnold_camera_metadata import ' \
                           'ValidateArnoldCameraMetadata; ValidateArnoldCameraMetadata().process(None)")'
        post_mel_current_value = lib.get_attribute('defaultRenderGlobals.postMel') or ''
        if post_mel_command not in post_mel_current_value:
            post_mel_command += '; ' + post_mel_current_value
            lib.set_attribute('postMel', post_mel_command, 'defaultRenderGlobals')
