from enum import Enum
import os
import logging

import pyblish.api

from openpype.hosts.photoshop import api as photoshop
from openpype.pipeline import OptionalPyblishPluginMixin
from openpype.settings import get_project_settings
from openpype.pipeline.publish import (
    ValidateContentsOrder,
    PublishXmlValidationError  
)


class ValidateNomenclatureRepair(pyblish.api.Action):
    """Repair the instance asset."""

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        stub = photoshop.stub()
        stub.rename_layers(context.data['transientData'][ValidateNomenclature.__name__])
    
        return True


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


def _generate_layer_with_id_name(layer_id, old_layer_name, new_layer_name):
    return {
        'id': layer_id,
        'previous_name': old_layer_name,
        'new_name': new_layer_name
    }


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
    active = True

    def process(self, context):
        if not self.is_active(context.data):
            return
        
        project_name = os.environ['AVALON_PROJECT']
        project_settings = get_project_settings(project_name)
        try:
            self.layers_types_colors = project_settings['fix_custom_settings']['photoshop']['layers_types_colors']
            self.layers_templates = project_settings['fix_custom_settings']['photoshop']['layers_templates']
        except KeyError as err:
            msg = "Layers types colors or templates has not been found in settings. ValidateNomenclature plugin can't be executed."
            logging.error(msg)
            logging.error(err)
            raise Exception

        stub = photoshop.stub()
        layers = stub.get_layers()
        layers.reverse()
        renamed_layers = list()

        for group_index, group_layer in enumerate(_extract_groups(layers), 1):
            renamed_group = self.rename_group(group_layer, group_index)
            if renamed_group: renamed_layers.append(renamed_group)

            for layer_index, layer in enumerate(_extract_layers_from_group(layers, group_layer), 1):
                renamed_layer = self.rename_layer(layer, group_index, layer_index)
                if renamed_layer: renamed_layers.append(renamed_layer)

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
        
    def rename_group(self, layer, group_index):
        return self._rename(
            entity_type="groups", 
            layer=layer, 
            group_index=group_index,
        )

    def rename_layer(self, layer, group_index, layer_index):
        return self._rename(
            entity_type="layers", 
            layer=layer, 
            group_index=group_index,
            layer_index=layer_index
        )

    def _rename(self, entity_type, layer, group_index, layer_index=None):
        template = None
        layer_type = self.layers_types_colors.get(layer.color_code, '??')
        overriden_templates = self.layers_templates.get(f'overriden_{entity_type}_templates')

        if overriden_templates:
            template = self._search_for_overriden_template(
                filters_set=overriden_templates,
                layer_type=layer_type
            )

        if not template:
            template = self.layers_templates.get(f"default_{entity_type}_template", None)

            if not template:
                logging.warning(f"Can't find template for given entity {entity_type}. Can't rename object.")
                return layer.name
    
        new_layer_name = template.format(
            **self._pack_layer_data(layer, layer_type, group_index, layer_index)
        )
        if new_layer_name == layer.name:
            return
        
        return _generate_layer_with_id_name(
            layer_id=layer.id,
            old_layer_name= layer.name,
            new_layer_name=new_layer_name
        )
    
    def _search_for_overriden_template(self, filters_set, **filter_data):
        "Browse filtering sets and check for each template if given filtering data met a filter set."
        "Return the first template which met all conditions, None if no ones does."
        for filter_set in filters_set:
            if not filter_set:
                continue

            only_valid_properties = False

            for filter_property_name, filter_value in filter_data.items():
                property_template_value = filter_set.get(filter_property_name)
                if not property_template_value:
                    continue

                if property_template_value == filter_value:
                    only_valid_properties = True

                else :
                    only_valid_properties = False
                    break

            if only_valid_properties:
                return filter_set.get('template', None)
        
        return None

    
    def _pack_layer_data(self, layer, layer_type, group_index, layer_index=None):
        packed_data = {
            'group_number': group_index,
            'type': layer_type,
            'layer_name': layer.name
        }
        if layer_index: 
            packed_data['layer_number'] = _convert_index_to_letter(layer_index)

        return packed_data
