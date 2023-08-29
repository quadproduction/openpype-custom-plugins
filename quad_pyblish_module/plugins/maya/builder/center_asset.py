from openpype.hosts.maya.api.plugin import BuilderAction
import maya.cmds as cmds


class CentrerAsset(BuilderAction):
    """An exemple Builder class with minimal required attributes
    """

    families = ["model"]
    representations = ["ma", "mb"]
    hosts = ["maya"]
    label = "Center Asset"

    def load(self, context, name=None, namespace=None, options=None):
        print(f"{'#' * 20} Center Asset {'#' * 20}")
        model = cmds.ls(assemblies=True)
        cameras = cmds.ls(type="camera")
        camera_objects = [cmds.listRelatives(camera, parent=True)[0] for camera in cameras if cmds.listRelatives(camera, parent=True)]

        renderable_camera = None
        filtered_model = []
        exclude_list = ['persp', 'top', 'front', 'side']
        exclude_list.extend(camera_objects)

        for element in model:
            if not any(exclude_elem in element for exclude_elem in exclude_list):
                filtered_model.append(element)

        for cam in camera_objects:
            if cmds.getAttr(cam + ".renderable"):
                shapes = cmds.listRelatives(
                    cam, parent=True, fullPath=True, type="transform")
                if shapes:
                    renderable_camera = shapes[0]
                    break

        if renderable_camera:
            cmds.lookThru(renderable_camera)

        cmds.viewFit(filtered_model, f=0.6)