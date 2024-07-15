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

class ImageCameraAdder(plugin.AssetLoader):
    """Add Image in Blender as background in camera.

    Create background image for active camera and assign selected image in a new background_images.
    """

    families = ["image", "render", "review"]
    representations = ["png"]

    label = "Add Image in Camera"
    icon = "code-fork"
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
        imported_image = bpy.data.images.load(image_filepath)

        camera = bpy.context.scene.camera
        if not camera:
            raise ValueError("No camera has been found in scene. Can't import image as camera background.")

        camera.data.show_background_images = True
        print (len(camera.data.background_images))
        try:
            background = camera.data.background_images[len(camera.data.background_images)]
        except IndexError:
            background = camera.data.background_images.new()        
        imported_image.source = 'FILE'
        background.source = 'IMAGE'
        background.image = imported_image

        self.log.info(f"Image at path {imported_image.filepath} has been correctly added in scene as camera background.")
