from datetime import datetime
import os
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer, Qgis

MESSAGE_CATEGORY = 'Swiss Geo Downloader'

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

def getDateFromIsoString(isoString):
    """Translate ISO date string to swiss date format"""
    if not isoString:
        return ''
    if isoString[-1] == 'Z':
        isoString = isoString[:-1]
    dt = datetime.fromisoformat(isoString)
    return dt.strftime('%d.%m.%Y')

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
    layerName = 'Swisstopo National Map (grey)'

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
            return f"Layer '{layerName}' added to map", Qgis.Success
        else:
            return f"Not able to add layer '{layerName}' to map", Qgis.Warning
    else:
        return f"Layer '{layerName}' already added to map", Qgis.Info
