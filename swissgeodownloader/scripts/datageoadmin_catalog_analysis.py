import os

from qgis.core import QgsApplication

from swissgeodownloader.api.apiCallerTask import ApiCallerTask
from swissgeodownloader.api.datageoadmin import ApiDataGeoAdmin
from swissgeodownloader.utils.metadataHandler import saveToFile


def refreshMetadata():
    api = ApiDataGeoAdmin(None)
    task = ApiCallerTask(api, None, '', {})
    api.refreshAllMetadata(task)


def analyseFullCatalog():
    api = ApiDataGeoAdmin(None)
    task = ApiCallerTask(api, None, '', {})
    items = api.catalogPropertiesCrawler(task)
    save(items)


def save(items):
    if items:
        savePath = os.path.join(os.path.dirname(__file__),
                                'datageoadmin_catalog_analysis.json')
        saveToFile(items, savePath)


def onError(error):
    print(error)


if __name__ == '__main__':
    # Get arguments from command line
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else None
    
    QGIS_APP = QgsApplication([], False)
    QGIS_APP.initQgis()
    
    if action == 'refreshMetadata':
        refreshMetadata()
    elif action == 'analyseFullCatalog':
        analyseFullCatalog()
