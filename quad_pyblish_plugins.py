import os
from openpype.modules import IPluginPaths


class QuadPyblishPlugins(IPluginPaths):
    name = "quadpyblish"

    @staticmethod
    def get_plugin_paths():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
