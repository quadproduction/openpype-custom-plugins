"""Render Layer and Passes creators.

Render layer is main part which is represented by group in TVPaint. All TVPaint
layers marked with that group color are part of the render layer. To be more
specific about some parts of layer it is possible to create sub-sets of layer
which are named passes. Render pass consist of layers in same color group as
render layer but define more specific part.

For example render layer could be 'Bob' which consist of 5 TVPaint layers.
- Bob has 'head' which consist of 2 TVPaint layers -> Render pass 'head'
- Bob has 'body' which consist of 1 TVPaint layer -> Render pass 'body'
- Bob has 'arm' which consist of 1 TVPaint layer -> Render pass 'arm'
- Last layer does not belong to render pass at all

Bob will be rendered as 'beauty' of bob (all visible layers in group).
His head will be rendered too but without any other parts. The same for body
and arm.

What is this good for? Compositing has more power how the renders are used.
Can do transforms on each render pass without need to modify a re-render them
using TVPaint.

The workflow may hit issues when there are used other blending modes than
default 'color' blend more. In that case it is not recommended to use this
workflow at all as other blend modes may affect all layers in clip which can't
be done.

There is special case for simple publishing of scene which is called
'render.scene'. That will use all visible layers and render them as one big
sequence.

Todos:
    Add option to extract marked layers and passes as json output format for
        AfterEffects.
"""

import collections
from typing import Any, Optional, Union

from openpype.client import get_asset_by_name
from openpype.lib import (
    prepare_template_data,
    AbstractAttrDef,
    UILabelDef,
    UISeparatorDef,
    EnumDef,
    TextDef,
    BoolDef,
)
from openpype.pipeline.create import (
    CreatedInstance,
    CreatorError,
)
from openpype.hosts.tvpaint.api.plugin import (
    TVPaintCreator,
    TVPaintAutoCreator,
)
from openpype.hosts.tvpaint.api.lib import (
    get_layers_data,
    get_groups_data,
    execute_george_through_file,
)

RENDER_LAYER_DETAILED_DESCRIPTIONS = (
    """Render Layer is "a group of TVPaint layers"

Be aware Render Layer <b>is not</b> TVPaint layer.

All TVPaint layers in the scene with the color group id are rendered in the
beauty pass. To create sub passes use Render Pass creator which is
dependent on existence of render layer instance.

The group can represent an asset (tree) or different part of scene that consist
of one or more TVPaint layers that can be used as single item during
compositing (for example).

In some cases may be needed to have sub parts of the layer. For example 'Bob'
could be Render Layer which has 'Arm', 'Head' and 'Body' as Render Passes.
"""
)


RENDER_PASS_DETAILED_DESCRIPTIONS = (
    """Render Pass is sub part of Render Layer.

Render Pass can consist of one or more TVPaint layers. Render Pass must
belong to a Render Layer. Marked TVPaint layers will change it's group color
to match group color of Render Layer.
"""
)


AUTODETECT_RENDER_DETAILED_DESCRIPTION = (
    """Semi-automated Render Layer and Render Pass creation.

Based on information in TVPaint scene will be created Render Layers and Render
Passes. All color groups used in scene will be used for Render Layer creation.
Name of the group is used as a variant.

All TVPaint layers under the color group will be created as Render Pass where
layer name is used as variant.

The plugin will use all used color groups and layers, or can skip those that
are not visible.

There is option to auto-rename color groups before Render Layer creation. That
is based on settings template where is filled index of used group from bottom
to top.
"""
)


class TVPaintSceneRenderCreator(TVPaintAutoCreator):
    family = "render"
    subset_template_family_filter = "playblast"
    identifier = "render.playblast"
    label = "Playblast"
    icon = "fa.file-image-o"

    # Settings
    default_pass_name = "beauty"
    mark_for_review = True
    active_on_create = False

    def apply_settings(self, project_settings, system_settings):
        plugin_settings = (
            project_settings["fix_custom_settings"]["tvpaint"]["create"]["create_playblast"]
        )
        self.default_variant = plugin_settings["default_variant"]
        self.default_variants =  plugin_settings["default_variants"]
        self.mark_for_review = True
        self.exports_types = ['camera', 'scene']
        self.export_type = self.exports_types[0]


    def _create_new_instance(self):
        create_context = self.create_context
        host_name = create_context.host_name
        project_name = create_context.get_current_project_name()
        asset_name = create_context.get_current_asset_name()
        task_name = create_context.get_current_task_name()

        asset_doc = get_asset_by_name(project_name, asset_name)
        subset_name = self.get_subset_name(
            self.default_variant,
            task_name,
            asset_doc,
            project_name,
            host_name
        )
        data = {
            "asset": asset_name,
            "task": task_name,
            "variant": self.default_variant,
            "creator_attributes": {
                "mark_for_review": True,
                "export_type": self.export_type
            },
            "label": self._get_label(subset_name)
        }
        data["active"] = False

        new_instance = CreatedInstance(
            self.family, subset_name, data, self
        )
        instances_data = self.host.list_instances()
        instances_data.append(new_instance.data_to_store())
        self.host.write_instances(instances_data)
        self._add_instance_to_context(new_instance)
        return new_instance

    def create(self):
        existing_instance = None
        for instance in self.create_context.instances:
            if instance.creator_identifier == self.identifier:
                existing_instance = instance
                break

        if existing_instance is None:
            return self._create_new_instance()

        create_context = self.create_context
        host_name = create_context.host_name
        project_name = create_context.get_current_project_name()
        asset_name = create_context.get_current_asset_name()
        task_name = create_context.get_current_task_name()

        if (
            existing_instance["asset"] != asset_name
            or existing_instance["task"] != task_name
        ):
            asset_doc = get_asset_by_name(project_name, asset_name)
            subset_name = self.get_subset_name(
                existing_instance["variant"],
                task_name,
                asset_doc,
                project_name,
                host_name,
                existing_instance
            )
            existing_instance["asset"] = asset_name
            existing_instance["task"] = task_name
            existing_instance["subset"] = subset_name

        existing_instance["label"] = self._get_label(existing_instance["subset"])

    def _get_label(self, subset_name):
        try:
            subset_name = subset_name.format(**prepare_template_data({}))
        except (KeyError, ValueError):
            pass

        return subset_name
    
    def get_dynamic_data(self, variant, *args, **kwargs):
        dynamic_data = super().get_dynamic_data(variant, *args, **kwargs)
        return dynamic_data

    def get_instance_attr_defs(self):
        return [
            EnumDef(
                "export_type",
                self.exports_types,
                label="Export type",
                default=self.export_type
            )
        ]
