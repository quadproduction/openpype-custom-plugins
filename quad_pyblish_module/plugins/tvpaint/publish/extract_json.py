"""Plugin exporting json file.
"""
import os
import tempfile
import json

import pyblish.api
from openpype.hosts.tvpaint.api import lib
from openpype.settings import get_project_settings


class ExtractJson(pyblish.api.ContextPlugin):
    """ Extract a JSON file and add it to the instance representation.
    """
    order = pyblish.api.ExtractorOrder + 0.01
    label = "Extract JSON"
    hosts = ["tvpaint"]

    project_name = os.environ['AVALON_PROJECT']
    project_settings = get_project_settings(project_name)

    enabled = project_settings['fix_custom_settings']['tvpaint']['publish'][
        'ExtractJson']['enabled']

    def process(self, context):

        # Create temp folder
        output_dir = (
            tempfile.mkdtemp(prefix="tvpaint_render_")
        ).replace("\\", "/")

        context.data["tvpaint_export_json"] = {"stagingDir": output_dir}

        context_data = context.data.get("tvpaint_export_json")
        self.log.info(context_data)

        self.log.info('Extract Json')
        # TODO: george script in list
        george_script_lines = "tv_clipsavestructure \"{}\" \"JSON\" \"onlyvisiblelayers\" \"true\" \"patternfolder\" \"{}\" \"patternfile\" \"{}\"".format(  # noqa
            os.path.join(output_dir, 'tvpaint'), "%ln", "%pfn_%ln.%4ii"
        )

        self.log.debug("Execute: {}".format(george_script_lines))
        lib.execute_george_through_file(george_script_lines)

        raw_json_path = os.path.join(output_dir, 'tvpaint.json')
        context_data['json_output_dir'] = output_dir
        context_data['raw_json_data_path'] = raw_json_path

        with open(raw_json_path) as tvpaint_json:
            tvpaint_data = json.load(tvpaint_json)

        context_data['tvpaint_layers_data'] = tvpaint_data['project']['clip']['layers']  # noqa
        instance_layer = [
            layer['name'] for layer in context.data.get('layersData')
        ]

        if context_data.get('instance_layers'):
            context_data['instance_layers'].extend(instance_layer)
        else:
            context_data['instance_layers'] = instance_layer

        tvpaint_data['project']['clip']['layers'] = []
        op_json_filename = 'openpype.json'
        op_json_path = os.path.join(output_dir, op_json_filename)
        with open(op_json_path, "w") as op_json:
            json.dump(tvpaint_data, op_json)

        json_repres = {
            "name": "json",
            "ext": "json",
            "files": op_json_filename,
            "stagingDir": output_dir,
            "tags": ["json_data"]
        }
        if context_data.get("representations"):
            context_data["representations"].append(json_repres)
        else:
            context_data["representations"] = [json_repres]

        self.log.info(context_data)

        self.log.debug("Add json representation: {}".format(json_repres))
