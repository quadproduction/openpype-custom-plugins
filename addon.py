import os
from openpype.modules import OpenPypeAddOn, IPluginPaths


class CustomPublishPlugins(OpenPypeAddOn, IPluginPaths):
    label = "Custom Publish Plugins"
    name = "custom_publish_plugins"

    def initialize(self, settings):
        self.enabled = True

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print('-'*100)
        print("current_dir :", os.path.join(current_dir, "plugins", "publish"))
        print('-'*100)
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
