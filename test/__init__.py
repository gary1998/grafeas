from flask_testing import TestCase
import connexion


class BaseTestCase(TestCase):
    def create_app(self):
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.add_api('swagger.yaml')
        return app.app
