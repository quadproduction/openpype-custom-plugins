import os

from openpype.modules import (
    OpenPypeAddOn,
    IPluginPaths,
)


class CustomPublishPlugins(OpenPypeAddOn, IPluginPaths):
    """This Addon has defined its settings and interface.

    This example has system settings with an enabled option. And use
    few other interfaces:
    - `IPluginPaths` to define custom plugin paths
    - `ITrayAction` to be shown in tray tool
    """
    label = "Custom Publish Plugins"
    name = "custom_publish_plugins"

    def initialize(self, settings):
        """Initialization of addon."""
        module_settings = settings[self.name]
        # Enabled by settings
        self.enabled = module_settings.get("enabled", False)

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        current_dir = os.path.dirname(os.path.abspath(__file__))

        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
