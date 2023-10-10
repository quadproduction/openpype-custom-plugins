import pyblish import api


class IntegrateVersionToTask(api.ContextPlugin):
    """Integrate Version To Task"""

    order = api.IntegratorOrder + 10.1
    hosts = ["hiero"]
    label = "Integrate Version To Task"
    optional = False

    def process(self, context):
        print('----------------------------------------')
        print('----------------------------------------')
        print('----------------------------------------')
        print('----------------------------------------')
        from pprint import pprint
        print(type(context))
        pprint(context.data)
        print('----------------------------------------')
        print('----------------------------------------')
        print('----------------------------------------')
        print('----------------------------------------')
