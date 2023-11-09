# This module has been backup because it also load in others DCC and
# it is not used anymore.

from openpype.client import get_asset_by_name
from openpype.pipeline import CreatedInstance
from openpype.pipeline.create import Creator


class TVPaintJsonCreator(Creator):
    families = ["imagesequence"]
    identifier = "imagesequence"
    label = "Json"
    icon = "fa.file-o"
    hosts = ["tvpaint"]

    def apply_settings(self, project_settings, system_settings):
        plugin_settings = (
            project_settings["fix_custom_settings"]["tvpaint"]["create"][
                "create_json"]
        )
        self.default_variant = plugin_settings["default_variant"]
        self.default_variants = plugin_settings["default_variants"]
        self.enabled = plugin_settings.get("enabled", True)

    def create(self, subset_name, instance_data, pre_create_data):
        existing_instance = None
        for instance in self.create_context.instances:
            if instance.creator_identifier == self.identifier:
                existing_instance = instance
                break

        create_context = self.create_context
        host_name = create_context.host_name
        project_name = create_context.get_current_project_name()
        asset_name = create_context.get_current_asset_name()
        task_name = create_context.get_current_task_name()

        if existing_instance is None:
            asset_doc = get_asset_by_name(project_name, asset_name)
            subset_name = self.get_subset_name(
                self.default_variant,
                task_name,
                asset_doc,
                project_name,
                host_name
            )
            data = {
                "asset": asset_name,
                "task": task_name,
                "variant": self.default_variant
            }

            new_instance = CreatedInstance(
                self.family, subset_name, data, self
            )
            instances_data = self.host.list_instances()
            instances_data.append(new_instance.data_to_store())
            self.host.write_instances(instances_data)
            self._add_instance_to_context(new_instance)

        elif (
            existing_instance["asset"] != asset_name
            or existing_instance["task"] != task_name
        ):
            asset_doc = get_asset_by_name(project_name, asset_name)
            subset_name = self.get_subset_name(
                existing_instance["variant"],
                task_name,
                asset_doc,
                project_name,
                host_name,
                existing_instance
            )
            existing_instance["asset"] = asset_name
            existing_instance["task"] = task_name
            existing_instance["subset"] = subset_name