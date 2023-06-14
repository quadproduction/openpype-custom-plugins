import logging
from maya import cmds
from collections import defaultdict
import time

from openpype.hosts.maya.api import lib
import openpype.hosts.maya.api.plugin
from openpype.hosts.maya.tools.mayalookassigner import (
    commands,
    vray_proxies,
    arnold_standin
)
from openpype.pipeline.context_tools import get_current_project_name
from openpype.client import get_last_version_by_subset_id

log = logging.getLogger(__name__)


class ApplyLook(openpype.hosts.maya.api.plugin.ReferenceLoader):
    families = ["look"]
    representations = ["ma", "mb"]
    hosts = ["maya"]

    label = "FixLookLoader"
    order = -10
    icon = "code-fork"
    color = "orange"

    def process_reference(self, context, name, namespace, options):
        import maya.cmds as cmds

        with lib.maintained_selection():
            file_url = self.prepare_root_value(self.fname,
                                               context["project"]["name"])
            nodes = cmds.file(file_url,
                              namespace=namespace,
                              reference=True,
                              returnNewNodes=True)

        self[:] = nodes

        self.apply_look()

    def apply_look(self):
        nodes = commands.get_all_asset_nodes()
        asset_nodes = commands.create_items_from_nodes(nodes)
        looks = set()

        for item in asset_nodes:
            for look in item['looks']:
                if look['name'] == "lookBasic":
                    looks.add(look['name'])

        self.process_looks(asset_nodes, looks)

    def process_looks(self, asset_nodes, looks):
        """Process all selected looks for the selected assets"""
        nodes = self.get_nodes(asset_nodes)

        project_name = get_current_project_name()
        start = time.time()
        for i, (asset, item) in enumerate(nodes.items()):

            # Label prefix
            prefix = "({}/{})".format(i + 1, len(nodes))

            # Assign the first matching look relevant for this asset
            # (since assigning multiple to the same nodes makes no sense)
            assign_look = next((subset for subset in item["looks"]
                                if subset["name"] in looks), None)

            if not assign_look:
                log.warning(
                    "{} No matching selected look for {}".format(prefix, asset)
                )
                continue

            # Get the latest version of this asset's look subset
            version = get_last_version_by_subset_id(
                project_name, assign_look["_id"], fields=["_id"]
            )

            subset_name = assign_look["name"]
            log.info("{} Assigning {} to {}\t".format(
                prefix, subset_name, asset
            ))
            nodes = item["nodes"]

            # Assign Vray Proxy look.
            if cmds.pluginInfo('vrayformaya', query=True, loaded=True):
                log.info("Getting vray proxy nodes ...")
                proxies = set(cmds.ls(type="VRayProxy", long=True))

                for vp in proxies:
                    if vp in nodes:
                        vray_proxies.vrayproxy_assign_look(vp, subset_name)

                nodes = list(set(nodes).difference(proxies))
            else:
                log.warning(
                    "Could not assign to VRayProxy because vrayformaya plugin "
                    "is not loaded."
                )

            # Assign Arnold Standin look.
            if cmds.pluginInfo("mtoa", query=True, loaded=True):
                arnold_standins = set(cmds.ls(type="aiStandIn", long=True))

                for standin in arnold_standins:
                    if standin in nodes:
                        arnold_standin.assign_look(standin, subset_name)

                nodes = list(set(nodes).difference(arnold_standins))
            else:
                log.warning(
                    "Could not assign to aiStandIn because mtoa plugin is not "
                    "loaded."
                )

            # Assign look
            if nodes:
                lib.assign_look_by_version(nodes, version_id=version["_id"])

        end = time.time()

        log.info("Finished assigning.. ({0:.3f}s)".format(end - start))

    def get_nodes(self, items):
        """Find the nodes in the current scene per asset."""

        nodes = cmds.ls(dag=True, long=True)
        id_nodes = commands.create_asset_id_hash(nodes)

        # Collect the asset item entries per asset
        # and collect the namespaces we'd like to apply
        assets = {}
        asset_namespaces = defaultdict(set)
        for item in items:
            asset_id = str(item["asset"]["_id"])
            asset_name = item["asset"]["name"]
            asset_namespaces[asset_name].add(item.get("namespace"))

            if asset_name in assets:
                continue

            assets[asset_name] = item
            assets[asset_name]["nodes"] = id_nodes.get(asset_id, [])

        # Filter nodes to namespace (if only namespaces were selected)
        for asset_name in assets:
            namespaces = asset_namespaces[asset_name]

            # When None is present there should be no filtering
            if None in namespaces:
                continue

            # Else only namespaces are selected and *not* the top entry so
            # we should filter to only those namespaces.
            nodes = assets[asset_name]["nodes"]
            nodes = [node for node in nodes if
                     commands.get_namespace_from_node(node) in namespaces]
            assets[asset_name]["nodes"] = nodes

        return assets
