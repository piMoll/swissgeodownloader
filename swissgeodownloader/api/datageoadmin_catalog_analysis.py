import os

from qgis.core import QgsApplication, QgsTask

from swissgeodownloader.api.apiCallerTask import ApiCallerTask
from swissgeodownloader.api.datageoadmin import ApiDataGeoAdmin
from swissgeodownloader.utils.metadataHandler import saveToFile


def refreshMetadata(apiDGA, msgBar):
    request = ApiCallerTask(apiDGA, msgBar, 'getAllDatasets')
    request.taskCompleted.connect(
        lambda: analyseFullCatalog(request.output, apiDGA, msgBar))
    request.taskTerminated.connect(
        lambda: analyseFullCatalog(None, apiDGA, msgBar))
    QgsApplication.taskManager().addTask(request)


def analyseFullCatalog(datasetList, apiDGA, msgBar):
    apiDGA = ApiDataGeoAdmin(None)
    request = QgsTask.fromFunction('test', apiDGA.catalogPropertiesCrawler,
                                   save)
    # request.taskCompleted.connect(
    #     lambda: save(request.output))
    # request.taskTerminated.connect(
    #     lambda: save(None))
    QgsApplication.taskManager().addTask(request)


def save(items):
    if items:
        savePath = os.path.join(os.path.dirname(__file__),
                                'datageoadmin_catalog_analysis.json')
        saveToFile(items, savePath)


if __name__ == '__main__':
    # Get arguments from command line
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else None
    api = ApiDataGeoAdmin(None)
    callerTask = ApiCallerTask(None)
    
    if action == 'refreshMetadata':
        ds = api.getDatasetList(callerTask)
    elif action == 'getDatasetFilters':
        ds = api.getDatasetList(callerTask)
        if ds:
            items = api.getAllFileLists(callerTask, ds)
