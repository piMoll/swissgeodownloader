import os
import tempfile

from qgis.core import QgsApplication
from qgis.testing import unittest

import swissgeodownloader

swissgeodownloader.DEBUG = True
    
QGIS_APP = QgsApplication([], False)
tmpdir = tempfile.mkdtemp('', 'QGIS-PythonTestConfigPath-')
os.environ['QGIS_CUSTOM_CONFIG_PATH'] = tmpdir

QGIS_APP.initQgis()


def stopTestRun(self):
    """Called once after all tests are executed."""
    if QGIS_APP:
        QGIS_APP.exitQgis()


setattr(unittest.TestResult, 'stopTestRun', stopTestRun)
