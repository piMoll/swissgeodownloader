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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsVectorLayer,
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPoint,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle
)
from qgis.gui import QgsMapCanvas

SWISSTOPO_WMS_URL = 'http://wms.geo.admin.ch/'
OVERVIEW_MAP = 'ch.swisstopo.pixelkarte-grau'
SWISS_CRS = 'EPSG:2056'
RECOMMENDED_CRS = ['EPSG:2056', 'EPSG:21781']


def tr(message, **kwargs):
    """Get the translation for a string using Qt translation API.
    We implement this ourselves since we do not inherit QObject.
    """
    return QCoreApplication.translate('@default', message)


def transformBbox(rectangle: QgsRectangle, transformer: QgsCoordinateTransform):
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


def addLayersToQgis(layers: list[QgsRasterLayer | QgsVectorLayer]):
    qgsProject = QgsProject.instance()
    for layer in layers:
        qgsProject.addMapLayer(layer)


def switchToCrs(canvas: QgsMapCanvas, crs=SWISS_CRS):
    newCrs = QgsCoordinateReferenceSystem(crs)
    assert newCrs.isValid()
    QgsProject.instance().setCrs(newCrs)
    canvas.refresh()


def addOverviewMap(canvas: QgsMapCanvas, crs=SWISS_CRS):
    qgsProject = QgsProject.instance()
    layerName = tr('Swisstopo National Map (grey)')
    wmsUrl = (f'contextualWMSLegend=0&crs={crs}&dpiMode=7'
              f'&featureCount=10&format=image/png'
              f'&layers={OVERVIEW_MAP}'
              f'&styles=&url={SWISSTOPO_WMS_URL}')
    
    already_added = [lyr.source() for lyr in qgsProject.mapLayers().values()]
    
    if wmsUrl not in already_added:
        wmsLayer = QgsRasterLayer(wmsUrl, layerName, 'wms')
        if wmsLayer.isValid():
            qgsProject.addMapLayer(wmsLayer)
            canvas.refresh()
            return tr("Layer '{}' added to map").format(
                layerName), Qgis.MessageLevel.Success
        else:
            return tr("Not able to add layer '{}' to map").format(
                layerName), Qgis.MessageLevel.Warning
    else:
        return tr("Layer '{}' already added to map").format(
            layerName), Qgis.MessageLevel.Info
    
