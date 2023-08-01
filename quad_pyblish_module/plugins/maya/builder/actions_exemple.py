from openpype.hosts.maya.api.plugin import BuilderAction


class ActionExemple(BuilderAction):
    """An exemple Builder class with minimal required attributes
    """

    families = ["model"]
    representations = ["ma", "mb"]
    hosts = ["maya"]
    label = "Exemple Action"

    def load(self, context, name=None, namespace=None, options=None):
        print(f"{'#' * 20} Exemple action {'#' * 20}")