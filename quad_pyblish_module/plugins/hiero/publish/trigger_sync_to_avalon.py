import pyblish.api
import ftrack_api

class IntegrateTriggerSyncToAvalon(pyblish.api.ContextPlugin):
    """ Triggers Avalon synchronization.
    """

    order = pyblish.api.IntegratorOrder + 10.2
    label = "Trigger Sync To Avalon Action"
    families = ["shot"]
    hosts = ["hiero"]

    def process(self, context):
        # we do this only if the collect hierarchy is done
        hierarchy_context = context.data.get("hierarchyContext")
        if not hierarchy_context:
            self.log.debug("Skipping {}".format(type(self).__name__))
            return

        session = context.data["ftrackSession"]

        event_data = {
            "actionIdentifier": "sync.to.avalon.server",
            "project_name": context.data["projectEntity"]["name"],
            "selection": [{
                "entityId": context.data["projectEntity"]["data"]["ftrackId"],
                "entityType": "show"
            }],
        }
        session.event_hub.connect()
        session.event_hub.publish(
            ftrack_api.event.base.Event(
                topic="ftrack.action.launch",
                data=event_data,
            ),
            on_error="ignore"
        )

