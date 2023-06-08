import os
import glob
from openpype.modules import OpenPypeModule, IPluginPaths


class QuadPyblishModule(OpenPypeModule, IPluginPaths):
    name = "quadpyblish"

    def __init__(self, manager, settings):
        self._api = None
        self.settings = settings
        super(QuadPyblishModule, self).__init__(manager, settings)

    def initialize(self, module_settings):
        self.enabled = True

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        # Regex to get all plugins from the plugins directory
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins', '**', '*.py')

        # Initialize all plugins which can be supported
        plugins_dict = {
            "publish": [],
            "load": [],
            "create": [],
            "actions": [],
        }

        # Find all plugins recursively
        for filepath in glob.glob(current_dir, recursive=True):
            if '__init__.py' in filepath:
                continue

            plugin_type = next((key for key in plugins_dict.keys() if key in filepath), None)

            if os.path.dirname(filepath) not in plugins_dict[plugin_type]:
                plugins_dict[plugin_type].append(os.path.dirname(filepath))

        return plugins_dict
