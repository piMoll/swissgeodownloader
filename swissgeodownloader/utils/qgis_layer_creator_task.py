"""
/***************************************************************************
 SwissGeoDownloader
                                 A QGIS plugin
 This plugin lets you comfortably download swiss geo data.
                             -------------------
        begin                : 2021-03-14
        copyright            : (C) 2025 by Patricia Moll
        email                : pimoll.dev@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from osgeo import gdal
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsRasterLayer,
    QgsTask,
    QgsVectorLayer,
    Qgis
)

from swissgeodownloader.api.response_objects import SgdAsset
from swissgeodownloader.utils.utilities import translate, log


def createQgisLayersInTask(fileList: list[SgdAsset], vrtOutputPath, callback):
    # Create layer from files (streamed and downloaded) so they can be
    # added to qgis
    task = QgisLayerCreatorTask(
            translate('SGD', 'Adding files to QGIS...'),
            fileList, vrtOutputPath)
    task.taskCompleted.connect(
            lambda: callback(task.layerList, task.alreadyAdded,
                             task.exception))
    task.taskTerminated.connect(lambda: callback([], 0, task.exception))
    QgsApplication.taskManager().addTask(task)
    
    
class QgisLayerCreatorTask(QgsTask):
    """ QGIS can freeze when a lot of layers have to be created in the main
     thread. Instead, layers are created in this separate QTask and moved to
     the main thread. After the task has finished, they are added to the map
     in the main thread."""
    
    def __init__(self, description, fileList: list[SgdAsset], vrtOutputPath):
        super().__init__(description, QgsTask.Flag.CanCancel)
        self.fileList = fileList
        self.layerList: list[QgsRasterLayer | QgsVectorLayer] = []
        self.alreadyAdded: int = 0
        self.exception = None
        self.vrtOutputPath = vrtOutputPath
    
    def run(self):
        
        if not self.fileList or len(self.fileList) == 0:
            return True
        
        qgsProject = QgsProject.instance()
        already_added = [lyr.source() for lyr in
                         qgsProject.mapLayers().values()]
        
        progressStep = 100 / len(self.fileList)
        
        if self.vrtOutputPath:
            return self.combineTiles()
        
        for i, file in enumerate(self.fileList):
            if self.isCanceled():
                return False
            
            self.setProgress(i * progressStep)
            
            # Adding the file to QGIS if it's (1) a streamed file or (2) is
            #  present in the file system and (3) is not a .zip
            if file.isStreamable or os.path.exists(file.path):
                if '.zip' in file.id:
                    # Can't add zip files to QGIS
                    continue
                if file.path in already_added:
                    self.alreadyAdded += 1
                    continue
                
                # Try to create a raster layer first, if that fails, create a
                #  vector layer
                success = self.createRasterLayer(file.path, file.id)
                if success:
                    continue
                
                self.createVectorLayer(file.path, file.id)
        return True
    
    def combineTiles(self):
        try:
            pathList = [file.path for file in self.fileList]
            gdal.BuildVRT(self.vrtOutputPath, pathList)
        except Exception as e:
            self.exception = str(e)
            return False
        layerName = os.path.splitext(os.path.basename(self.vrtOutputPath))[0]
        return self.createRasterLayer(self.vrtOutputPath, layerName)
    
    def createRasterLayer(self, filepath, filename):
        try:
            rasterLyr = QgsRasterLayer(filepath, filename)
            if rasterLyr.isValid():
                self.layerList.append(rasterLyr)
                return True
            else:
                del rasterLyr
        except Exception as e:
            self.exception = f'{filename}: {e}' if self.exception is None else self.exception + f'\n{filename}: {e}'
        return False
    
    def createVectorLayer(self, filepath, filename):
        try:
            vectorLyr = QgsVectorLayer(filepath, filename, "ogr")
            if vectorLyr.isValid():
                self.layerList.append(vectorLyr)
                return True
            else:
                del vectorLyr
        except Exception as e:
            self.exception = f'{filename}: {e}' if self.exception is None else self.exception + f'\n{filename}: {e}'
        return False
    
    def finished(self, result):
        self.setProgress(100)
        if not result:
            if self.isCanceled():
                self.exception = self.tr('Aborted by user')
            elif self.exception is None:
                self.exception = self.tr('An unknown error occurred')
        for e in str(self.exception).split('\n'):
            log(e, Qgis.MessageLevel.Warning)
