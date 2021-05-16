import os
import json

from qgis.PyQt.QtCore import QEventLoop, QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsTask, QgsNetworkContentFetcher, QgsFileDownloader

BASEURL = 'https://data.geo.admin.ch/api/stac/v0.9/collections'
API_EPSG = 'EPSG:4326'
OPTION_MAPPER = {
    'coordsys': 'proj:epsg',
    'resolution': 'eo:gsd',
    'format': 'geoadmin:variant',
}
API_OPTION_MAPPER =  {y:x for x,y in OPTION_MAPPER.items()}


class ApiDataGeoAdmin:
    
    def __init__(self, parent):
        self.baseUrl = BASEURL
        self.parent = parent
        self.fetcher = QgsNetworkContentFetcher()
        self.task = None
    
    def getDatasetList(self, task: QgsTask):
        """Get a list of all available datasets and read out with options the
        dataset supports"""
        collection = self.fetch(self.baseUrl, task)
        
        if not collection or not isinstance(collection, dict) \
                or 'collections' not in collection:
            task.exception = 'Error when loading available dataset - Did not understand API response'
            return False
        
        datasetList = {}
        for ds in collection['collections']:
            
            if task.isCanceled():
                return False
            
            dataset = {
                'id': ds['id'],
                'bbox': ds['extent']['spatial']['bbox'][0],
                'links': {
                    'files': [link['href'] for link in ds['links']
                              if link['rel'] == 'items'][0],
                    'meta': [link['href'] for link in ds['links']
                             if link['rel'] == 'describedby'][0],
                    'license': [link['href'] for link in ds['links']
                                if link['rel'] == 'license'][0],
                },
                'options': {}
            }
            options = {}
            for sumName, sumItem in ds['summaries'].items():
                options[API_OPTION_MAPPER[sumName]] = sumItem
            
            # Get available timestamps
            if 'temporal' in ds['extent']:
                timestamps = ds['extent']['temporal']['interval'][0]
                # Remove empty values
                timestampList = [ts for ts in timestamps if ts]
                if timestampList:
                    options['timestamp'] = timestampList
                    options['timestamp'].reverse()
            
            dataset['options'] = options
            datasetList[dataset['id']] = dataset
        
        return datasetList
    
    def getDatasetDetails(self, task: QgsTask, dataset):
        """Analyse dataset to figure out available options in gui"""
        url = dataset['links']['files']
        # Get max. 40 features
        items = self.fetch(url, task, {'limit' : 40})

        fileCount = 0
        useBBox = True
        
        if items and isinstance(items, dict) and 'features' in items:
            fileCount = len(items['features'])
            
            # Check if it makes sense to select by bbox
            if fileCount <= 1 or ('timestamp' in dataset['options']
                and fileCount == len(dataset['options']['timestamp'])):
                useBBox = False
            
            # TODO Check tile size to warn user for big download sizes
            # firstItem = items['features'][0]
            # bbox = firstItem['extent']['spatial']['bbox'][0]
        
        return {'selectByBBox': useBBox, 'isEmpty': fileCount == 0}

    def getFileList(self, task: QgsTask, dataset, bbox, timestamp, options):
        """Request a list of available files that are within a bounding box and
        have a specified timestamp"""
        params = {}
        if bbox:
            params['bbox'] = ','.join([str(ext) for ext in bbox])
        if timestamp:
            params['datetime'] = timestamp
    
        url = dataset['links']['files']
        items = self.fetch(url, task, params=params)
    
        # Filter list
        fileList = []

        if not items or not isinstance(items, dict) \
                or not 'features' in items:
            task.exception = 'Error when requesting file list - Did not understand API response'
            return False
            
        for item in items['features']:
            # Filter assets so that we only get the one file that matches the
            #  defined options
            for assetId in item['assets']:
        
                if task.isCanceled():
                    return False
        
                file = {}
                asset = item['assets'][assetId]
        
                # Filter out all files that match the specified options
                optionsMatch = []
                for optionName, optionValue in options.items():
                    optionApiName = OPTION_MAPPER[optionName]
            
                    optionsMatch.append(optionApiName in asset.keys() and
                                        optionValue == asset[
                                            optionApiName])
        
                if sum(optionsMatch) == len(optionsMatch):
                    file['id'] = assetId
                    file['type'] = asset['type']
                    file['href'] = asset['href']
            
                    # Analyse file extension
                    extension = os.path.splitext(assetId)[1]
                    file['ext'] = extension
            
                    # Get Metadata if this file
                    # TODO: Write method to fetch header info
                    # meta = getFileMetadata(file['href'])
                    # file['size'] = int(meta.headers['Content-Length'])
                    file['size'] = 1024
            
                    fileList.append(file)

        return fileList
    
    def fetch(self, url, task: QgsTask, params=None, header=None):
        request = QNetworkRequest()
        # Prepare url
        callUrl = QUrl(url)
        if params:
            queryParams = QUrlQuery()
            for key, value in params.items():
                queryParams.addQueryItem(key, str(value))
            callUrl.setQuery(queryParams)
        request.setUrl(callUrl)
        
        if header:
            request.setHeader(*tuple(header))

        task.log(f'Start request {callUrl.toString()}')
        self.fetcher.fetchContent(callUrl)
        
        # Run fetcher in separate event loop
        eventLoop = QEventLoop()
        self.fetcher.finished.connect(eventLoop.quit)
        eventLoop.exec_(QEventLoop.ExcludeUserInputEvents)
        self.fetcher.finished.disconnect(eventLoop.quit)
        
        # Check if request was successful
        r = self.fetcher.reply()
        assert r.error() == QNetworkReply.NoError, r.error()
        
        # Process response
        try:
            return json.loads(self.fetcher.contentAsString())
        
        except json.JSONDecodeError as e:
            task.exception = str(e)
            return False

    def downloadFiles(self, task: QgsTask, fileList, outputDir):
        task.setProgress(0)
        step = 100 / len(fileList)
        
        for file in fileList:
            if task.isCanceled():
                return False
        
            savePath = os.path.join(outputDir, file['id'])
            self.fetchFile(task, file['href'], file['id'], savePath)
            task.setProgress(task.progress() + step)
        return True
    
    def fetchFile(self, task: QgsTask, url, filename, filePath, params=None):
        # Prepare url
        callUrl = QUrl(url)
        if params:
            queryParams = QUrlQuery()
            for key, value in params.items():
                queryParams.addQueryItem(key, str(value))
            callUrl.setQuery(queryParams)
        
        task.log(f'Start download of {callUrl.toString()}')
        fileFetcher = QgsFileDownloader(callUrl, filePath)
        
        def onCancel():
            task.exception = f'Download of {filename} was canceled'
            return False
        def onError():
            task.exception = f'Error when downloading {filename}'
            return False
        
        # Run file download in separate event loop
        eventLoop = QEventLoop()
        fileFetcher.downloadError.connect(onError)
        fileFetcher.downloadCanceled.connect(onCancel)
        fileFetcher.downloadCompleted.connect(eventLoop.quit)
        eventLoop.exec_(QEventLoop.ExcludeUserInputEvents)
        fileFetcher.downloadCompleted.disconnect(eventLoop.quit)



