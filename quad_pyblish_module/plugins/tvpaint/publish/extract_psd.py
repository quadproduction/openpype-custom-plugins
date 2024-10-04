"""Plugin exporting psd files.
"""
import os
import json
import tempfile
from pathlib import Path

import pyblish.api
import logging
from openpype.settings import get_project_settings
from openpype.hosts.tvpaint.api import lib


class ExtractPsd(pyblish.api.InstancePlugin):
    order = pyblish.api.ExtractorOrder + 0.02
    label = "Extract PSD"
    hosts = ["tvpaint"]
    families = ["renderLayer", "review", "render"]

    project_name = os.environ['AVALON_PROJECT']
    project_settings = get_project_settings(project_name)

    enabled = project_settings['quad_custom_settings']['hosts']['tvpaint']['publish'][
        'ExtractPsd'].get('enabled', False)

    staging_dir_prefix = "tvpaint_export_json_psd_"

    def process(self, instance):
        if not self.enabled:
            return

        if not instance.data["creator_attributes"].get("extract_psd", False):
            return

        george_script_lines = []
        # Sorting repre to only take the png once
        # This is directly link to the extract process of tvpaint
        repres = [repre for repre in instance.data.get("representations") if repre['name'] == 'png']
        if not repres:
            return
        
        scene_mark_in = int(instance.context.data["sceneMarkIn"])
        scene_mark_out = int(instance.context.data["sceneMarkOut"])
        scene_start_frame = int(instance.context.data["sceneStartFrame"])
        output_dir = instance.data.get("stagingDir")

        export_frames = instance.data.get("exportFrames")
        custom_mark_range = instance.data.get("ExportFramesWithoutOffset", [])

        if custom_mark_range:
            scene_mark_in = min(custom_mark_range)
            scene_mark_out = max(custom_mark_range)

        if output_dir:
            # Only convert to a Path object if not None or empty
            output_dir = Path(output_dir)

        if not output_dir or not output_dir.exists():
            # Create temp folder if staging dir is not set
            output_dir = Path(tempfile.mkdtemp(
                prefix=self.staging_dir_prefix).replace("\\", "/"))
            instance.data['stagingDir'] = str(output_dir.resolve())

        new_psd_repres = []
        for repre in repres:

            self.log.info("Processing representation: {}".format(
                json.dumps(repre, sort_keys=True, indent=4)
            ))

            filenames = repre['files']

            if type(filenames) != list:
                filenames = [filenames]       
            
            # Update the enumerate_files if custom index or frame_range is given    
            enumerate_files = zip(list(range(scene_mark_in, scene_mark_out+1)), filenames)

            new_filenames = []
            for frame_index, filename in enumerate_files:
                new_filename = Path(filename).stem
                dst_filepath = output_dir.joinpath(new_filename)
                new_filenames.append(new_filename + '.psd')
                # george command to export psd files for each image
                george_script_lines.append(
                    "tv_clipsavestructure \"{}\" \"PSD\" \"image\" {}".format(
                        dst_filepath.resolve(),
                        frame_index
                    )
                )

            # Convert list to str if there's only one item
            if len(new_filenames) == 1:
                new_filenames = new_filenames[0]

            new_psd_repres.append(
                {
                    "name": "psd",
                    "ext": "psd",
                    "files": new_filenames,
                    "stagingDir": str(output_dir.resolve()),
                    "tags": "psd"
                }
            )

        lib.execute_george_through_file("\n".join(george_script_lines))

        instance.data["representations"].extend(new_psd_repres)

        self.log.info(
            "Representations: {}".format(
                json.dumps(
                    instance.data["representations"], sort_keys=True, indent=4
                )
            )
        )
