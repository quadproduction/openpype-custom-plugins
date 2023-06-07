import os
from openpype.modules import OpenPypeModule, IPluginPaths


class QuadPyblishModule(OpenPypeModule, IPluginPaths):
    name = "quadpyblish"

    def __init__(self, manager, settings):
        super(QuadPyblishModule, self).__init__(manager, settings)

    def initialize(self, module_settings):
        self.enabled = True

    @staticmethod
    def get_plugin_paths():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print('-'*100)
        print("current_dir :", os.path.join(current_dir, "plugins", "publish"))
        print('-'*100)
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
