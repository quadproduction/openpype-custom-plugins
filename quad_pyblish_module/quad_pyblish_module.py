import os
from pathlib import Path
from openpype.modules import (
    OpenPypeModule,
    IPluginPaths,
    JsonFilesSettingsDef
)


class QuadPyblishModule(OpenPypeModule, IPluginPaths):
    name = "quadpyblish"
    _valid_plugin_types = ["publish", "load", "create", "actions", "inventory", "builder"]

    def __init__(self, manager, settings):
        self._api = None
        self.settings = settings
        self._plugin_folders = {}
        super(QuadPyblishModule, self).__init__(manager, settings)

    def initialize(self, module_settings):
        self.enabled = True

    def get_plugin_folders(self, regenerate_cache=False):
        if self._plugin_folders and not regenerate_cache:
            return self._plugin_folders

        parent_folder_path = Path(__file__).parent.joinpath("plugins")

        hosts_folders_iterator = parent_folder_path.glob('*/')
        for host_folder_path in hosts_folders_iterator:
            host_name = host_folder_path.stem

            if host_name not in self._plugin_folders:
                self._plugin_folders[host_name] = {}

            for plugin_type_path in host_folder_path.glob('*/'):
                type_name = plugin_type_path.stem

                if type_name not in self._valid_plugin_types:
                    continue

                if type_name not in self._plugin_folders[host_name]:
                    self._plugin_folders[host_name][type_name] = []

                self._plugin_folders[host_name][type_name].append(str(plugin_type_path.absolute()))

        return self._plugin_folders

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        plugin_folders = self.get_plugin_folders()

        # Initialize all plugins which can be supported
        plugins_dict = {type_name: [] for type_name in self._valid_plugin_types}

        for host_name in plugin_folders:
            for type_name in plugin_folders[host_name]:
                if type_name in plugins_dict:
                    plugins_dict[type_name].extend(plugin_folders[host_name][type_name])

        return plugins_dict

    def get_plugin_paths_by_hostnames_and_type(self, host_names, type_name):
        plugins_paths = []

        plugin_folders = self.get_plugin_folders()

        if isinstance(host_names, str):
            host_names = [host_names]

        for host_name in host_names:
            if host_name in plugin_folders and type_name in plugin_folders[host_name]:
                plugins_paths.extend(plugin_folders[host_name][type_name])

        return plugins_paths

    def get_create_plugin_paths(self, host_name):
        return self.get_plugin_paths_by_hostnames_and_type([host_name, "common"], "create")

    def get_load_plugin_paths(self, host_name):
        return self.get_plugin_paths_by_hostnames_and_type([host_name, "common"], "load")

    def get_publish_plugin_paths(self, host_name):
        return self.get_plugin_paths_by_hostnames_and_type([host_name, "common"], "publish")

    def get_inventory_action_paths(self, host_name):
        return self.get_plugin_paths_by_hostnames_and_type([host_name, "common"], "inventory")

    def get_builder_action_paths(self, host_name):
        return self.get_plugin_paths_by_hostnames_and_type([host_name, "common"], "builder")


class AddonSettingsDef(JsonFilesSettingsDef):
    # This will add prefixes to every schema and template from `schemas`
    #   subfolder.
    # - it is not required to fill the prefix but it is highly
    #   recommended as schemas and templates may have name clashes across
    #   multiple addons
    # - it is also recommended that prefix has addon name in it
    schema_prefix = "quad_custom_settings"

    def get_settings_root_path(self):
        """Implemented abstract class of JsonFilesSettingsDef.

        Return directory path where json files defying addon settings are
        located.
        """
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "settings"
        )
