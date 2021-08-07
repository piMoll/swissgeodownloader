"""
/***************************************************************************
 SwissGeoDownloader
                                 A QGIS plugin
 This plugin lets you comfortably download swiss geo data.
                             -------------------
        begin                : 2021-03-14
        copyright            : (C) 2021 by Patricia Moll
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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, Qgis,
                       QgsRectangle, QgsPoint)


def tr(message, **kwargs):
    """Get the translation for a string using Qt translation API.
    We implement this ourselves since we do not inherit QObject.
    """
    return QCoreApplication.translate('@default', message)


def transformBbox(rectangle: QgsRectangle, transformer):
    llCoord = (rectangle.xMinimum(), rectangle.yMinimum())
    urCoord = (rectangle.xMaximum(), rectangle.yMaximum())
    
    # Cancel if there are no actual coords in input fields
    if not all(llCoord) or not all(urCoord):
        return []
    
    llPoint = QgsPoint(*tuple(llCoord))
    urPoint = QgsPoint(*tuple(urCoord))
    llPoint.transform(transformer)
    urPoint.transform(transformer)
    return [llPoint.x(),
            llPoint.y(),
            urPoint.x(),
            urPoint.y()]


def addToQgis(fileList):
    # # Create new layer group in table of content
    # root = QgsProject.instance().layerTreeRoot()
    # projGroup = root.insertGroup(0, projName)

    already_added = [lyr.source() for lyr in
                     QgsProject.instance().mapLayers().values()]

    for file in fileList:
        if os.path.exists(file['path']) and not '.zip' in file['ext']:
            if file['path'] in already_added:
                continue
            try:
                rasterLyr = QgsRasterLayer(file['path'], file['id'])
                if rasterLyr.isValid():
                    QgsProject.instance().addMapLayer(rasterLyr)
                    continue
                else:
                    del rasterLyr
            except Exception:
                pass
            try:
                vectorLyr = QgsVectorLayer(file['path'], file['id'], "ogr")
                if vectorLyr.isValid():
                    QgsProject.instance().addMapLayer(vectorLyr)
                    continue
                else:
                    del vectorLyr
            except Exception:
                pass


def addOverviewMap(canvas, crs):
    swisstopoUrl = 'http://wms.geo.admin.ch/'
    swisstopoOverviewMap = 'ch.swisstopo.pixelkarte-grau'
    layerName = tr('Swisstopo National Map (grey)')
    
    wmsUrl = (f'contextualWMSLegend=0&crs={crs}&dpiMode=7'
              f'&featureCount=10&format=image/png'
              f'&layers={swisstopoOverviewMap}'
              f'&styles=&url={swisstopoUrl}')
    
    already_added = [lyr.source() for lyr in
                     QgsProject.instance().mapLayers().values()]
    
    if wmsUrl not in already_added:
        wmsLayer = QgsRasterLayer(wmsUrl, layerName, 'wms')
        if wmsLayer.isValid():
            QgsProject.instance().addMapLayer(wmsLayer)
            canvas.refresh()
            return tr("Layer '{}' added to map").format(
                layerName), Qgis.Success
        else:
            return tr("Not able to add layer '{}' to map").format(
                layerName), Qgis.Warning
    else:
        return tr("Layer '{}' already added to map").format(
            layerName), Qgis.Info
    