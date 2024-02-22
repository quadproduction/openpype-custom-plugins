"""Load an asset in Blender from an Alembic file."""

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

class ImageVideo(plugin.AssetLoader):
    """Load FBX models.

    Stores the imported asset in an empty named after the asset.
    """

    families = ["image", "render", "review"]
    representations = ["mp4", "avi", "h264_mp4"]

    label = "Load Video"
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
        video_filepath = self.filepath_from_context(context)
        imported_video = bpy.data.movieclips.load(video_filepath)

        camera = bpy.context.scene.camera
        if not camera:
            raise ValueError("No camera has been found in scene. Can't import video as camera background.")

        camera.data.show_background_images = True
        try:
            background = camera.data.background_images[0]
        except IndexError:
            background = camera.data.background_images.new()

        background.source = 'MOVIE_CLIP'
        background.clip = imported_video

        self.log.info(f"Video at path {imported_video.filepath} has been correctly loaded in scene as camera background.")
