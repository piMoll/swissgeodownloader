import os
import sys
import tempfile
from qgis.core import QgsApplication
from qgis.testing import unittest
import SwissGeoDownloader

SwissGeoDownloader.DEBUG = True
TEST_DIR = os.path.dirname(__file__)
TESTDATA_DIR = os.path.join(TEST_DIR, 'testdata')
TMP_DIR = os.path.join(TESTDATA_DIR, 'tmp')

if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
    
    
QGIS_APP = QgsApplication([], False)
tmpdir = tempfile.mkdtemp('', 'QGIS-PythonTestConfigPath-')
os.environ['QGIS_CUSTOM_CONFIG_PATH'] = tmpdir

QGIS_APP.initQgis()


def stopTestRun(self):
    """Called once after all tests are executed."""
    if QGIS_APP:
        QGIS_APP.exitQgis()


setattr(unittest.TestResult, 'stopTestRun', stopTestRun)
