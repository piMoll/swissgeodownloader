import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject, QgsRasterLayer, QgsTask, QgsVectorLayer)

from .. import DEBUG
from ..api.responseObjects import STREAMED_SOURCE_PREFIX


class QgisLayerCreatorTask(QgsTask):
    """ QGIS can freeze when a lot of layers have to be created in the main
     thread. Instead, layers are created in this separate QTask and moved to
     the main thread. After the task has finished, they are added to the map
     in the main thread."""
    
    def __init__(self, description, fileList):
        super().__init__(description, QgsTask.Flag.CanCancel)
        self.fileList = fileList
        self.layerList = []
        self.exception = None
    
    def run(self):
        if DEBUG:
            try:
                # Add pydevd to path
                import sys
                sys.path.insert(0,
                                '/snap/pycharm-professional/current/debug-eggs/pydevd-pycharm.egg')
                import pydevd_pycharm
                pydevd_pycharm.settrace('localhost', port=53100, suspend=False,
                                        stdoutToServer=True,
                                        stderrToServer=True)
            except ConnectionRefusedError:
                pass
            except ImportError:
                pass
        
        qgsProject = QgsProject.instance()
        already_added = [lyr.source() for lyr in
                         qgsProject.mapLayers().values()]
        
        progressStep = 100 / len(self.fileList)
        
        for i, file in enumerate(self.fileList):
            self.setProgress(i * progressStep)
            
            # Adding the file to QGIS if it's (1) a streamed file or (2) is
            #  present in the file system and (3) is not a .zip
            if (file.path.startswith(STREAMED_SOURCE_PREFIX) or os.path.exists(
                    file.path)) and '.zip' not in file.id:
                if file.path in already_added:
                    continue
                try:
                    rasterLyr = QgsRasterLayer(file.path, file.id)
                    if rasterLyr.isValid():
                        self.layerList.append(rasterLyr)
                        rasterLyr.moveToThread(
                            QCoreApplication.instance().thread())
                        continue
                    else:
                        del rasterLyr
                except Exception:
                    pass
                try:
                    vectorLyr = QgsVectorLayer(file.path, file.id, "ogr")
                    if vectorLyr.isValid():
                        self.layerList.append(vectorLyr)
                        vectorLyr.moveToThread(
                            QCoreApplication.instance().thread())
                        continue
                    else:
                        del vectorLyr
                except Exception:
                    pass
        
        self.setProgress(100)
        return True
    
    def finished(self, result):
        if not result:
            if self.isCanceled():
                self.exception = self.tr('Aborted by user')
            elif self.exception is None:
                self.exception = self.tr('An unknown error occurred')
