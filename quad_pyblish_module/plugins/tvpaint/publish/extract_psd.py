"""Plugin exporting psd files.
"""
import os
import json
import tempfile
from pathlib import Path

import pyblish.api
from openpype.settings import get_project_settings
from openpype.hosts.tvpaint.api import lib


class ExtractPsd(pyblish.api.InstancePlugin):
    order = pyblish.api.ExtractorOrder + 0.02
    label = "Extract PSD"
    hosts = ["tvpaint"]
    families = ["renderLayer", "review", "render"]

    project_name = os.environ['AVALON_PROJECT']
    project_settings = get_project_settings(project_name)

    enabled = project_settings['fix_custom_settings']['tvpaint']['publish'][
        'ExtractPsd'].get('enabled', False)

    staging_dir_prefix = "tvpaint_export_json_psd_"

    def process(self, instance):
        if not self.enabled:
            return

        if not instance.data["creator_attributes"].get("extract_psd", False):
            return

        george_script_lines = []
        repres = instance.data.get("representations")
        if not repres:
            return
        
        scene_mark_in = int(instance.context.data["sceneMarkIn"])
        output_dir = instance.data.get("stagingDir")

        if output_dir:
            # Only convert to a Path object if not None or empty
            output_dir = Path(output_dir)

        if not output_dir or not output_dir.exists():
            # Create temp folder if staging dir is not set
            output_dir = Path(tempfile.mkdtemp(
                prefix=self.staging_dir_prefix).replace("\\", "/"))
            instance.data['stagingDir'] = output_dir.resolve()

        new_psd_repres = []
        for repre in repres:
            if repre['name'] != 'png':
                continue

            self.log.info("Processing representation: {}".format(
                json.dumps(repre, sort_keys=True, indent=4)
            ))

            if not isinstance(repre['files'], list):
                files = [repre['files']]
            else:
                files = repre['files']

            new_filenames = []
            for offset, filename in enumerate(files):
                new_filename = Path(filename).stem
                dst_filepath = output_dir.joinpath(new_filename)
                new_filenames.append(new_filename + '.psd')

                frame_start = self.get_frame_start(repre)

                # george command to export psd files for each image
                george_script_lines.append(
                    "tv_clipsavestructure \"{}\" \"PSD\" \"image\" {}".format(
                        dst_filepath.resolve(),
                        scene_mark_in + offset
                    )
                )

            # Convert list to str if there's only one item
            if len(new_filenames) == 1:
                new_filenames = "".join(new_filenames)

            new_psd_repres.append(
                {
                    "name": "psd",
                    "ext": "psd",
                    "files": new_filenames,
                    "stagingDir": output_dir.resolve(),
                    "tags": "psd"
                }
            )

        lib.execute_george_through_file("\n".join(george_script_lines))

        instance.data["representations"].extend(new_psd_repres)
        print('### REPRESENTATIONS')
        print(instance.data["representations"])
        self.log.info(
            "Representations: {}".format(
                json.dumps(
                    instance.data["representations"], sort_keys=True, indent=4
                )
            )
        )

    def get_frame_start(self, representation):
        frame_start = representation.get('frameStart')
        if not frame_start:
            frame_start = str(lib.execute_george("tv_startframe"))

        return frame_start
