import os
import unittest
import logging
import configparser

LOGGER = logging.getLogger('QGIS')


class TestInit(unittest.TestCase):
    """Test that the plugin init is usable for QGIS."""
    
    @classmethod
    def setUpClass(cls):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass

    def test_read_init(self):
        """Test that the plugin __init__ will validate on plugins.qgis.org."""

        required_metadata = [
            'name',
            'description',
            'version',
            'qgisMinimumVersion',
            'email',
            'author']

        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), os.pardir,
            'metadata.txt'))
        LOGGER.info(file_path)
        metadata = []
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(file_path)
        message = 'Cannot find a section named "general" in %s' % file_path
        assert parser.has_section('general'), message
        metadata.extend(parser.items('general'))

        for expectation in required_metadata:
            message = ('Cannot find metadata "%s" in metadata source (%s).' % (
                expectation, file_path))
            self.assertIn(expectation, dict(metadata), message)


if __name__ == '__main__':
    unittest.main()
