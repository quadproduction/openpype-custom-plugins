import os
from openpype.modules import IPluginPaths


class QuadPyblishPlugins(IPluginPaths):
    name = "quadpyblish"

    def get_plugin_paths(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
