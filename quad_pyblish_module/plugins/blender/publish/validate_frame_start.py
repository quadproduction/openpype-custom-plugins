import bpy

import pyblish.api

import openpype.hosts.blender.api.action
from openpype.pipeline.publish import ValidateContentsOrder
from openpype.pipeline import (
    PublishXmlValidationError,
    OptionalPyblishPluginMixin,
)


class ValidateFrameStart(
    OptionalPyblishPluginMixin,
    pyblish.api.ContextPlugin):
    """Ensure frameStart is equal to the value wanted by OpenPype."""

    order = ValidateContentsOrder
    hosts = ["blender"]
    families = ["*"]
    label = "Frame Start"
    actions = [openpype.hosts.blender.api.action.SelectInvalidAction]
    optional = True

    def process(self, context):
        registered_frame_start = context.data.get('frameStart', None)
        if registered_frame_start is None:
            raise RuntimeError(
                "Can't retrieve frame start information from OpenPype."
            )
        scene_frame_start = bpy.context.scene.frame_start
        if registered_frame_start != scene_frame_start:
            raise RuntimeError(
                f"Frame start for scene ({scene_frame_start}) if different from OpenPype's frame start ({registered_frame_start}).)"
            )
