"""Load an asset in Blender from an Alembic file."""

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

class ImageReferenceLoader(plugin.AssetLoader):
    """Load Image in Blender as reference.

    Create image in empty and put it in _REF collection.
    """

    families = ["image", "render", "review"]
    representations = ["png"]

    label = "Load Image as Reference"
    icon = "calendar-plus-o"
    color = "yellow"

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
        asset = context["asset"]["name"]

        imported_image = bpy.data.images.load(image_filepath)
        image_name = asset + '_null'

        empty = bpy.data.objects.new(image_name, None)
        empty.empty_display_type = "IMAGE"
    
        ref_collection = bpy.data.collections.get("_REF")
        if not ref_collection:
            ref_collection = bpy.data.collections.new(name="_REF")
            bpy.context.scene.collection.children.link(ref_collection)
        ref_collection.objects.link(empty)

        empty.data = imported_image

        self.log.info(f"Image at path {imported_image.filepath} has been correctly loaded in scene as reference.")
