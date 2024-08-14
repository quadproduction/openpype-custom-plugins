from pathlib import Path
from pprint import pformat
from typing import Dict, List, Optional

import bpy

from openpype.pipeline import (
    get_representation_path,
    AVALON_CONTAINER_ID,
)
from openpype.hosts.blender.api import plugin, lib
from openpype.hosts.blender.api.pipeline import (
    AVALON_CONTAINERS,
    AVALON_PROPERTY,
)

def blender_camera_bg_sequence_importer(image_filepath, context, reload = False):
    """
    Will add or reload an image sequence in the camera background

    image_filepath: path to the image to load
    context(dict): Full parenthood of representation to load
    reload(bool): If False will add an image background, if True, will replace the last imported image background
    """
    
    imported_image = bpy.data.images.load(image_filepath)

    camera = bpy.context.scene.camera
    if not camera:
        raise ValueError("No camera has been found in scene. Can't import image as camera background.")

    camera.data.show_background_images = True
    try:
        background = camera.data.background_images[len(camera.data.background_images) - reload]
    except IndexError:
        background = camera.data.background_images.new()        
    imported_image.source = 'SEQUENCE'
    background.source = 'IMAGE'
    background.image = imported_image
    background.image_user.frame_duration

    context_data = context.get('version', []).get('data', [])
    if not context_data:
        raise ValueError("Can't access to context data when retrieving frame informations. Abort.")

    frame_start = context_data.get('frameStart')
    frame_end = context_data.get('frameEnd')
    if not frame_start or not frame_end:
        raise ValueError("Can't find frame range informations. Abort.")

    frames = (frame_end - frame_start) + 1
    
    background.image_user.frame_start = frame_start
    background.image_user.frame_duration = frames
    background.image_user.frame_offset = 0

    print(f"Image sequence at path {imported_image.filepath} has been correctly loaded in scene as camera background.")

class ImageSequenceLoader(plugin.AssetLoader):
    """Replace Last Image Sequence in Blender in the last imported one.

    Create or Replace background image sequence for active camera and assign selected images in the last imported one.
    """

    families = ["image", "render"]
    representations = ["png"]

    label = "Replace Last Image Sequence"
    icon = "refresh"
    color = "orange"

    def process_asset(
        self, context: dict, name: str, namespace: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Optional[List]:
    
        """
        Arguments:
            name: Use pre-defined name
            namespace: Use pre-defined namespace
            context: Full parenthood of representation to load
            options: Additional settings dictionary
        """
        image_filepath = self.filepath_from_context(context)
        blender_camera_bg_sequence_importer(image_filepath, context, reload=True)

class ImageSequenceAdder(plugin.AssetLoader):
    """Add Image Sequence in Blender.

    Add background image sequence for active camera and assign selected images.
    """

    families = ["image", "render"]
    representations = ["png"]

    label = "Add Image Sequence"
    icon = "window-restore"
    color = "green"

    def process_asset(
        self, context: dict, name: str, namespace: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Optional[List]:
    
        """
        Arguments:
            name: Use pre-defined name
            namespace: Use pre-defined namespace
            context: Full parenthood of representation to load
            options: Additional settings dictionary
        """
        image_filepath = self.filepath_from_context(context)
        blender_camera_bg_sequence_importer(image_filepath, context, reload=False)
