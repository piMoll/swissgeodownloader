from datetime import datetime
import os
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer

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
            except Exception as e:
                pass
            try:
                vectorLyr = QgsVectorLayer(file['path'], file['id'], "ogr")
                if vectorLyr.isValid():
                    QgsProject.instance().addMapLayer(vectorLyr)
                    continue
                else:
                    del vectorLyr
            except Exception as e:
                pass
