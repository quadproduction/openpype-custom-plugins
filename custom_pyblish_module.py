import os
from openpype.modules import OpenPypeModule, IPluginPaths


class CustomPyblishModule(OpenPypeModule, IPluginPaths):
    name = "custom_pyblish_module"

    def __init__(self, manager, settings):
        self.rr_paths = {}
        self._api = None
        self.settings = settings
        super(CustomPyblishModule, self).__init__(manager, settings)

    def initialize(self, module_settings):
        custom_pyblish_settings = module_settings[self.name]
        self.enabled = custom_pyblish_settings["enabled"]
        self.rr_paths = custom_pyblish_settings.get("rr_paths")

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print('-'*100)
        print("current_dir :", os.path.join(current_dir, "plugins", "publish"))
        print('-'*100)
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
