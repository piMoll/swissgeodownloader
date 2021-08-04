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
from datetime import datetime
import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer, Qgis

MESSAGE_CATEGORY = 'Swiss Geo Downloader'


def tr(message, **kwargs):
    """Get the translation for a string using Qt translation API.
    We implement this ourselves since we do not inherit QObject.
    """
    return QCoreApplication.translate('@default', message)


def formatCoordinate(number):
    """Format big numbers with thousand separator, swiss-style"""
    if number is None:
        return ''
    # Format big numbers with thousand separator
    elif number >= 1000:
        return f"{number:,.0f}".replace(',', "'")
    else:
        return f"{number:,.6f}"
    

def castToNum(formattedNum):
    """Casts formatted numbers back to floats"""
    if type(formattedNum) in [int, float]:
        return formattedNum
    try:
        num = float(formattedNum.replace("'", ''))
    except (ValueError, AttributeError):
        num = None
    return num


def filesizeFormatter(num, suffix='B'):
    """Formats data sizes to human readable units"""
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def getDateFromIsoString(isoString, formatted=True):
    """Translate ISO date string to date or swiss date format"""
    if type(isoString) != str or not isoString:
        return ''
    if isoString[-1] == 'Z':
        isoString = isoString[:-1]
    try:
        dt = datetime.fromisoformat(isoString)
    except ValueError as e:
        return None
    if formatted:
        return dt.strftime('%d.%m.%Y')
    else:
        return dt


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
            return tr("Layer '{}' added to map").format(layerName), Qgis.Success
        else:
            return tr("Not able to add layer '{}' to map").format(layerName), Qgis.Warning
    else:
        return tr("Layer '{}' already added to map").format(layerName), Qgis.Info
