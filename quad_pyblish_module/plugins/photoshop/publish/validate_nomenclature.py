from enum import Enum
import os
import logging
import re

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
    active = False

    def process(self, context):
        if not self.is_active(context.data):
            return
        
        project_name = os.environ['AVALON_PROJECT']
        project_settings = get_project_settings(project_name)

        try:
            self.types_colors = project_settings['quad_custom_settings']['hosts']['photoshop']['types_colors']
            self.groups_templates = project_settings['quad_custom_settings']['hosts']['photoshop']['groups']['templates']
            self.layers_templates = project_settings['quad_custom_settings']['hosts']['photoshop']['layers']['templates']
            self.groups_expressions = project_settings['quad_custom_settings']['hosts']['photoshop']['groups']['expressions']
            self.layers_expressions = project_settings['quad_custom_settings']['hosts']['photoshop']['layers']['expressions']

        except KeyError as err:
            msg = "Types colors, templates or expressions are missing from settings. ValidateNomenclature plugin can't be executed."
            logging.error(msg)
            logging.error(err)
            raise Exception

        stub = photoshop.stub()
        layers = stub.get_layers()
        layers.reverse()
        renamed_layers = list()

        for group_index, group_layer in enumerate(_extract_groups(layers), 1):

            renamed_group = self.rename_group_if_needed(group_layer, group_index)
            if renamed_group: renamed_layers.append(renamed_group)

            for layer_index, layer in enumerate(_extract_layers_from_group(layers, group_layer), 1):

                renamed_layer = self.rename_layer_if_needed(layer, group_index, layer_index)
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
        
    def rename_group_if_needed(self, group_layer, group_index):
        renamed_group = None
        group_template = self.get_groups_template(group_layer)

        if not self.validate_group_name(group_template, group_layer.name):
            renamed_group = self.rename(group_template, group_layer, group_index)

        return renamed_group

    def rename_layer_if_needed(self, layer, group_index, layer_index):
        renamed_layer = None
        layer_template = self.get_layers_template(layer)

        if not self.validate_layer_name(layer_template, layer.name):
            renamed_layer = self.rename(layer_template, layer, group_index, layer_index)

        return renamed_layer

    def get_groups_template(self, group):
        return self._get_template(
            templates=self.groups_templates,
            layer=group
        )

    def get_layers_template(self, layer):
        return self._get_template(
            templates=self.layers_templates,
            layer=layer
        )
        
    def _get_template(self, templates, layer):
        template = None
        overriden_templates = templates.get(f'overriden')

        if overriden_templates:
            template = self._search_for_overriden_template(
                filters_set=overriden_templates,
                layer_type=self.types_colors.get(layer.color_code, '??')
            )

        if not template:
            template = templates.get(f"default", None)

            if not template:
                logging.warning(f"Can't find template correct template for layer {layer.name}. Can't rename it.")
                return layer.name
            
        return template

    def validate_group_name(self, template, group_name):
        return self._validate_name(
            template=template,
            layer_name=group_name,
            expressions=self.groups_expressions
        )
    
    def validate_layer_name(self, template, layer_name):
        return self._validate_name(
            template=template,
            layer_name=layer_name,
            expressions=self.layers_expressions
        )
    
    def _validate_name(self, template, layer_name, expressions):
        template = self._remove_format_specifications(template)
        template_regex = template.format(**expressions)
        return re.compile(template_regex).match(layer_name)
        
    def _remove_format_specifications(self, template):
        return re.sub(
            pattern=r'(:)(.*?)(?=})',
            repl='',
            string=template
        )

    def rename(self, template, layer, group_index, layer_index=None):
        layer_type = self.types_colors.get(layer.color_code, '??')

        # Removing all whitespace characters
        layer.name = re.sub(r'\s+', '', layer.name)

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
