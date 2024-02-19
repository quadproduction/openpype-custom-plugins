# -*- coding: utf-8 -*-
import re
import gazu
import pyblish.api


class IntegrateKitsuSequence(pyblish.api.InstancePlugin):
    """Integrate Kitsu Sequence"""

    order = pyblish.api.IntegratorOrder + 0.02
    label = "Kitsu Sequence"
    families = ["render", "kitsu"]
    optional = True

    def process(self, instance):
        # Check comment has been created
        comment_id = instance.data.get("kitsu_comment", {}).get("id")
        if not comment_id:
            self.log.debug(
                "Comment not created, review not pushed to preview."
            )
            return
        
        # Skip if Publish Sequence option hasn't been enabled from creator subset.
        if not instance.data.get("creator_attributes") or \
            not instance.data["creator_attributes"].get("publish_sequence"):
            self.log.debug(
                "Integrate Kitsu Sequence has not been enabled."
            )
            return

        # Add review representations as preview of comment
        task_id = instance.data["kitsu_task"]["id"]
        
        for representation in instance.data.get("representations", []):
            # Skip if Extract Sequence has interpreted image generation 
            # as review (before video concatenation) instead of a simple sequence.
            if "sequence" not in representation.get("tags", []):
                continue

            filesnames = representation.get("files")

            #if only one frame is publish, transform representation["files"] into a list qith a single element
            if type(filesnames) != list:
                filesnames = [filesnames]

            if not filesnames:
                self.log.warning("No files found following sequence extract.")
                raise IndexError       
                 
            extension = representation.get("ext")
            if not extension:
                self.log.warning("No extension found in representation.")
                raise IndexError

            published_path = representation.get("published_path")
            if not published_path:
                self.log.warning("No publish path found in representation.")
                raise IndexError
            
            for filename in filesnames:
                image_filepath = _generate_files_paths(published_path, extension, filename)
                gazu.task.add_preview(
                    task_id, comment_id, image_filepath, normalize_movie=True
                )

            self.log.info("{} images has been uploaded to Kitsu.".format(len(filesnames)))


def _generate_files_paths(published_path, extension, filename):
    return re.sub("\d{4}."+extension, filename, published_path)
