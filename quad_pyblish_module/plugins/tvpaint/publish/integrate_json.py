import os
import sys
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
            instance_representations = instance.data.get('representations')
            for repre in instance_representations:
                if repre['name'] == "json":
                    self._move_json_file(repre)

    def _move_json_file(self, representation):
        published_path, file_name = os.path.split(representation['published_path'])
        new_path = os.path.split(published_path)

        # Copy json file a folder up and delete old folder
        shutil.move(representation['published_path'], new_path[0])
        shutil.rmtree(published_path)

        new_published_path = os.path.join(new_path[0], file_name)
        representation['published_path'] = new_published_path
