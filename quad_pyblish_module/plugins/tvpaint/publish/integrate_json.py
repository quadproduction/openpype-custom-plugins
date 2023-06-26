import os
import json
import shutil

import pyblish.api
from openpype.settings import get_project_settings


class IntegrateJson(pyblish.api.ContextPlugin):
    """Integrate a JSON file."""

    label = "Integrate Json File"
    order = pyblish.api.IntegratorOrder + 0.05

    hosts = ["tvpaint"]

    project_name = os.environ['AVALON_PROJECT']
    project_settings = get_project_settings(project_name)

    enabled = project_settings['fix_custom_settings']['tvpaint']['publish'][
        'ExtractJson']['enabled']

    def process(self, context):
        for instance in context:
            json_repre = None
            instance_representations = instance.data.get('representations')
            for repre in instance_representations:
                if repre['name'] == "json":
                    json_repre = repre
                    self._move_json_file(repre)

                if "tags" in repre.keys() and "json_png" in repre["tags"]:
                    self.log.info("REPRE_NAME: {}".format(repre['name']))
                    self._modify_file_names(repre, json_repre)

    def _move_json_file(self, representation):
        published_path, file_name = os.path.split(representation['published_path'])
        new_path = os.path.split(published_path)

        # Copy json file a folder up and delete old folder
        shutil.move(representation['published_path'], new_path[0])
        shutil.rmtree(published_path)

        new_published_path = os.path.join(new_path[0], file_name)
        representation['published_path'] = new_published_path

    def _modify_file_names(self, representation, json_repre):
        published_path = representation["published_path"]
        file_basename = os.path.basename(published_path).split(".")[0]

        json_path = json_repre["published_path"]
        with open(json_path) as tvpaint_json:
            tvpaint_data = json.load(tvpaint_json)

        for layer in tvpaint_data['project']['clip']['layers']:
            if layer['name'] == representation['name']:
                for link in layer['link']:
                    link_basename = os.path.basename(link['file'])
                    old_name = link_basename.split(".")[0]
                    link['file'] = link['file'].replace(old_name, file_basename)

        # Write the modifications in the json file
        with open(json_path, "w") as new_json:
            new_json.seek(0)
            json.dump(tvpaint_data, new_json, indent=4)
            new_json.truncate()

