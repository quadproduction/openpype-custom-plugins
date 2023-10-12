from pyblish import api


class IntegrateVersionToTask(api.ContextPlugin):
    """Integrate Version To Task"""

    order = api.IntegratorOrder + 10.1
    hosts = ["hiero"]
    families = ["clip"]
    label = "Integrate Version To Task"
    optional = False

    def get_all_task_types(self, project):
        """Get all task types from the project schema.

        :param project: The Ftrack project Entity.
        :type project: ftrack Project Object
        :return: A dictionary containing all task types.
        :rtype: dict<ftrackTaskType>

        """
        tasks = {}
        proj_template = project['project_schema']
        temp_task_types = proj_template['_task_type_schema']['types']

        for type in temp_task_types:
            if type['name'] not in tasks:
                tasks[type['name']] = type

        return tasks

    def process(self, context):
        """Process the Pyblish context.

        :param context: The Pyblish context.
        :type context: pyblish.api.Context
        """
        # Get Data we need
        task_type = context.data.get('task').lower()
        ftrack_session = context.data.get('ftrackSession')
        ftrack_project = context.data.get('ftrackProject')
        ftrack_task_types = self.get_all_task_types(ftrack_project)

        if ftrack_session is None:
            self.log.info('Ftrack session is not created.')
            return

        # Build Plugin dict list to analyze
        to_analyze_lst = []
        for result_dict in context.data.get('results'):
            if 'Collect OTIO Review' in result_dict['plugin'].label:
                to_analyze_lst.append(result_dict)

        for to_analyze in to_analyze_lst:
            ftrack_shot_version = to_analyze['instance'].data['ftrackEntity']
            ftrack_asset_versions = to_analyze['instance'].data['ftrackIntegratedAssetVersions']

            # Check if confo task already exists in ftrack
            is_task_exist = ftrack_session.query(
                'Task where name is "{0}" and parent.id is {1}'.format(task_type, ftrack_shot_version['id'])).first()
            if not is_task_exist:
                new_task = ftrack_session.create(
                    'Task',
                    {
                        'name': task_type,
                        'parent': ftrack_shot_version,
                        'type': ftrack_task_types[task_type]
                    }
                )
            else:
                new_task = is_task_exist

            ftrack_session.commit()

            # Link Publish version to Task
            for asset_version in ftrack_asset_versions:
                asset_version['task'] = new_task

            ftrack_session.commit()
