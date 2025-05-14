import unittest
import os

from qgis.PyQt.QtCore import QCoreApplication, QTranslator


class TestSafeTranslations(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if 'LANG' in iter(os.environ.keys()):
            os.environ.__delitem__('LANG')

    def tearDown(self):
        """Runs after each test."""
        if 'LANG' in iter(os.environ.keys()):
            os.environ.__delitem__('LANG')

    def test_qgis_translations(self):
        """Test that translations work."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.join(
            dir_path, 'i18n', 'de.qm')
        translator = QTranslator()
        translator.load(file_path)
        QCoreApplication.installTranslator(translator)

        expected_message = 'Swisstopo Landeskarte (grau)'
        real_message = QCoreApplication.translate("@default", 'Swisstopo National Map (grey)')
        self.assertEqual(real_message, expected_message)


if __name__ == '__main__':
    unittest.main()
