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
    families = ["imagesequence"]

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

        self.log.info('Extract Json')
        # TODO: george script in list
        george_script_lines = "tv_clipsavestructure \"{}\" \"JSON\" \"onlyvisiblelayers\" \"true\" \"patternfolder\" \"{}\" \"patternfile\" \"{}\"".format(  # noqa
            os.path.join(output_dir, 'tvpaint'), "%ln", "%pfn_%ln.%4ii"
        )

        self.log.debug("Execute: {}".format(george_script_lines))
        lib.execute_george_through_file(george_script_lines)

        raw_json_path = os.path.join(output_dir, 'tvpaint.json')
        files_path = self.get_files(raw_json_path)

        instance_layer = [
            layer['name'] for layer in context.data.get('layersData')
        ]
        self.log.info("INSTANCE_LAYER: {}".format(instance_layer))

        if context_data.get('instance_layers'):
            context_data['instance_layers'].extend(instance_layer)
        else:
            context_data['instance_layers'] = instance_layer

        # self.log.info(context_data)

        json_repres = {
            "name": "json",
            "ext": "json",
            "files": "tvpaint.json",
            "stagingDir": output_dir,
            "tags": ["json"]
        }

        for instance in context:
            if instance.data.get('family') == 'imagesequence':
                instance.data.get('representations').append(json_repres)
            self.log.info("REPRESENTATIONS: {}".format(instance.data.get('representations')))

        """if context_data.get("representations"):
            context_data["representations"].append(json_repres)
        else:
            context_data["representations"] = [json_repres]"""

        self.log.debug("Add json representation: {}".format(json_repres))

    def get_files(self, json_path):
        all_links = []
        with open(json_path) as tvpaint_json:
            tvpaint_data = json.load(tvpaint_json)

        layers = tvpaint_data['project']['clip']['layers']
        for layer in layers:
            links = [l['file'] for l in layer['link']]
            all_links.append(links)

        return all_links
