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
            if not any(tag in ["sequence", "single_frame"] for tag in representation.get("tags", [])):
                continue

            filenames = representation.get("files")

            # If only one frame force a list
            if type(filenames) != list:
                filenames = [filenames]

            if not filenames:
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

            if "burnin" in representation.get("tags", []):
                filenames = ["{:04d}.{}".format(index + 1, extension) for index, file in enumerate(filenames)]

            for filename in filenames:
                image_filepath = _rename_output_filepath(published_path, extension, filename)
                gazu.task.add_preview(
                    task_id, comment_id, image_filepath, normalize_movie=True
                )

            self.log.info("{} images has been uploaded to Kitsu.".format(len(filenames)))


def _rename_output_filepath(published_path, extension, filename):
    # Replace frame number + extension in given filepath with new filename
    return re.sub(r"\d{4}\." + re.escape(extension), filename, published_path)
