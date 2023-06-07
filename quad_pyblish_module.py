import os
from openpype.modules import OpenPypeModule, IPluginPaths


class QuadPyblishModule(OpenPypeModule, IPluginPaths):
    name = "quadpyblish"

    def __init__(self, manager, settings):
        self._api = None
        self.settings = settings
        super(QuadPyblishModule, self).__init__(manager, settings)

    def initialize(self, module_settings):
        quad_pyblish_settings = module_settings[self.name]
        self.enabled = quad_pyblish_settings["enabled"]

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
