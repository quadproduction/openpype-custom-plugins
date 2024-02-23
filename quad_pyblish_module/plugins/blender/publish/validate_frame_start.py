from typing import List

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
    """Camera must have a keyframe at frame 0.

    Unreal shifts the first keyframe to frame 0. Forcing the camera to have
    a keyframe at frame 0 will ensure that the animation will be the same
    in Unreal and Blender.
    """

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
