from django.test.simple import DjangoTestSuiteRunner

class ByPassableDBDjangoTestSuiteRunner(DjangoTestSuiteRunner):

    def setup_databases(self, **kwargs):
        from django.db import connections
        old_names = []
        mirrors = []
        for alias in connections:
            connection = connections[alias]
            if not connection.settings_dict.get('USE_LIVE_FOR_TESTS', False):
                old_names.append((connection,
                                  connection.settings_dict['NAME']))
                connection.creation.create_test_db(self.verbosity)

        return old_names, mirrors

    def teardown_databases(self, old_config):
        pass