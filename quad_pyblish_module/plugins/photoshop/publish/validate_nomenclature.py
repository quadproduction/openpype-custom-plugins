from enum import Enum

import pyblish.api

from openpype.hosts.photoshop import api as photoshop
from openpype.pipeline import OptionalPyblishPluginMixin
from openpype.pipeline.publish import (
    ValidateContentsOrder,
    PublishXmlValidationError  
)

from .common import ColorMatches


class ValidateNomenclatureRepair(pyblish.api.Action):
    """Repair the instance asset."""

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        stub = photoshop.stub()
        stub.rename_layers(context.data['transientData'][ValidateNomenclature.__name__])
    
        return True


def _guess_group_prefix_from_color_code(layer, numbering):
    return 'XX' if layer.color_code in [ColorMatches.REF.value, ColorMatches.UTIL.value] else f'{numbering*10:03d}'


def _convert_index_to_letter(index):
    return chr(ord('`')+index)


def _extract_groups(layers):
    return [
        layer for layer in layers
        if layer.group == True
    ]


def _extract_layers_from_group(layers, group_layer):
    return [
        layer for layer in layers
        if layer.parents and
        layer.parents[0] == group_layer.id
    ]


def _extract_list_of_id_names(layers):
    return [
        { 
            'id': layer.id,
            'name': layer.name
        } for layer in layers
    ]


def _generate_layer_with_id_name(layer_id, old_layer_name, new_layer_name):
    return {
        'id': layer_id,
        'previous_name': old_layer_name,
        'new_name': new_layer_name
    }


def rename_group(layer, numbering, renamed_layers):
    prefix = _guess_group_prefix_from_color_code(layer, numbering)
    group_name = ColorMatches(layer.color_code).name
    new_layer_name = f'{prefix}_{group_name}'

    if new_layer_name == layer.name:
        return
    
    renamed_layers.append(
        _generate_layer_with_id_name(
            layer_id=layer.id,
            old_layer_name= layer.name,
            new_layer_name=new_layer_name
        )
    )


def rename_layer(layer, numbering, layer_index, renamed_layers):
    prefix = _guess_group_prefix_from_color_code(layer, numbering)
    letter_index = _convert_index_to_letter(layer_index)
    group_name = ColorMatches(layer.color_code).name
    new_layer_name = f'{prefix}_{letter_index}_{group_name}_{layer.name}'

    if new_layer_name == layer.name:
        return
    
    renamed_layers.append(
        _generate_layer_with_id_name(
            layer_id=layer.id,
            old_layer_name= layer.name,
            new_layer_name=new_layer_name
        )
    )


class ValidateNomenclature(
        OptionalPyblishPluginMixin,
        pyblish.api.ContextPlugin
    ):
    """Validate the instance name.

    Spaces in names are not allowed. Will be replace with underscores.
    """

    label = "Validate Nomenclature"
    hosts = ["photoshop"]
    order = ValidateContentsOrder
    families = ["image"]
    actions = [ValidateNomenclatureRepair]
    optional = True    
    active = False

    def process(self, context):
        if not self.is_active(context.data):
            return

        stub = photoshop.stub()
        layers = stub.get_layers()
        layers.reverse()
        renamed_layers = list()

        for numbering, group_layer in enumerate(_extract_groups(layers), 1):
            rename_group(group_layer, numbering, renamed_layers)

            for layer_index, layer in enumerate(_extract_layers_from_group(layers, group_layer), 1):
                rename_layer(layer, numbering, layer_index, renamed_layers)

        if renamed_layers:
            number_of_layers = len(renamed_layers)
            msg = (
                f"{number_of_layers} layers need to be renamed :\n" + \
                '\n'.join([layer['previous_name'] + ' -> ' + layer['new_name'] for layer in renamed_layers])
            )

            repair_msg = (
                f"Repair with 'Repair' button to automatically renamed all {number_of_layers} layers.'.\n"
            )
            formatting_data = {"msg": msg,
                               "repair_msg": repair_msg}
            
            if not context.data.get('transientData'):
                context.data['transientData'] = dict()

            context.data['transientData'][self.__class__.__name__] = renamed_layers

            raise PublishXmlValidationError(self, msg,
                                            formatting_data=formatting_data)
