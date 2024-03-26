import pyblish.api


class CollectAssetFramesData(pyblish.api.ContextPlugin):
    """Collect asset frames data into context."""

    order = pyblish.api.CollectorOrder - 0.099
    label = "Collect Asset Frames Data"

    def process(self, context):
        asset_entity = context.data["assetEntity"]

        if asset_entity['type'] != 'asset':
            self.log.info("Given entity is not of type asset. Frames values will not be overridden.")
            return
        
        asset_entity_data = asset_entity['data']

        metadata_in = asset_entity_data.get('in', None)
        if metadata_in is not None:
            self.log.info("'In' value found for given asset in asset entity metadatas. Will replace default frameStart value.")
            context.data['frameStart'] = int(metadata_in)

        metadata_out = asset_entity_data.get('out')
        if metadata_out is not None:
            self.log.info("'Out' value found for given asset in asset entity metadatas. Will replace default frameEnd value.")
            context.data['frameEnd'] = int(metadata_out)
