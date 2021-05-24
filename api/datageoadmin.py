import os
import json
import requests

from qgis.PyQt.QtCore import QEventLoop, QUrl, QUrlQuery, QCoreApplication
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import (QgsTask, QgsFileDownloader, QgsBlockingNetworkRequest,
                       Qgis)
from ..ui.ui_utilities import getDateFromIsoString

BASEURL = 'https://data.geo.admin.ch/api/stac/v0.9/collections'
API_EPSG = 'EPSG:4326'
OPTION_MAPPER = {
    'coordsys': 'proj:epsg',
    'resolution': 'eo:gsd',
    'format': 'geoadmin:variant',
}
API_OPTION_MAPPER = {y:x for x,y in OPTION_MAPPER.items()}
CUSTOM_OPTION_FILE = os.path.join(os.path.dirname(__file__), 'datageoadmin.json')
VERSION = Qgis.QGIS_VERSION_INT


class ApiDataGeoAdmin:
    
    def __init__(self, parent):
        self.baseUrl = BASEURL
        self.parent = parent
        self.http = QgsBlockingNetworkRequest()
        self.task = None
    
    def getDatasetList(self, task: QgsTask):
        """Get a list of all available datasets and read out with options the
        dataset supports"""
        collection = self.fetch(task, self.baseUrl)
        
        if not collection or not isinstance(collection, dict) \
                or 'collections' not in collection:
            task.exception = self.tr('Error when loading available dataset - '
                                     'Unexpected API response')
            return False

        # Read out custom overwrites for dataset options from a config file
        customOptions = self.getCustomOptions()
        
        datasetList = {}
        for ds in collection['collections']:
            
            if task.isCanceled():
                return False

            # Check if there are overwrites for this dataset
            custom = None
            if ds['id'] in customOptions:
                custom = customOptions[ds['id']]
            
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
                # Remove duplicates
                timestampList = list(set(timestampList))
                if timestampList:
                    # Create date object from string, insert timestamp into dict
                    dictOfDates = {getDateFromIsoString(ts, False): ts for ts in timestampList}
                    # Sort by date and return original timestamp
                    options['timestamp'] = [dictOfDates[tsKey] for tsKey in sorted(dictOfDates.keys())]
                    # Reverse sorting to get most current date first
                    options['timestamp'].reverse()
                
                    # Apply overwrites for timestamps
                    if (custom and 'options' in custom
                        and 'timestamp' in custom['options']
                        and custom['options']['timestamp'] == 'first'):
                        options['timestamp'] = [options['timestamp'][0]]

            dataset['options'] = options
            datasetList[dataset['id']] = dataset
        
        return datasetList
    
    def getDatasetDetails(self, task: QgsTask, dataset):
        """Analyse dataset to figure out available options in gui"""
        url = dataset['links']['files']
        # Get max. 40 features
        items = self.fetch(task, url, params={'limit' : 40})

        fileCount = 0
        useBBox = True
        estimate = {}
        
        if items and isinstance(items, dict) and 'features' in items:
            fileCount = len(items['features'])
            
            # Check if it makes sense to select by bbox
            # TODO: this should also check options and see, if there is only
            #  one file per option (e.g. farbe-pk100)
            if fileCount <= 1 or ('timestamp' in dataset['options']
                and fileCount == len(dataset['options']['timestamp'])):
                useBBox = False
            
            # Analyze size of an item to estimate download sizes later on
            if fileCount > 0:
                item = items['features'][-1]
                
                # Get an estimate of file size
                for assetId in item['assets']:
                    asset = item['assets'][assetId]
                    # Don't request again if we have this estimate already
                    if asset['type'] in estimate.keys():
                        continue
                    # Check Content-Length header
                    if VERSION >= 31800:
                        # Make a HEAD request to get the file size
                        header = self.fetch(task, asset['href'], method='head')
                        if header and header.hasRawHeader(b'Content-Length'):
                            estimate[asset['type']] = int(header.rawHeader(b'Content-Length'))
                    else:
                        # If QGIS version is below 3.18, use library 'requests'
                        # to make a HEAD request
                        header = self.fetchHeadLegacy(task, asset['href'])
                        if header:
                            estimate[asset['type']] = int(header.headers['Content-Length'])
        
        return {'selectByBBox': useBBox, 'isEmpty': fileCount == 0,
                'size': estimate}

    def getFileList(self, task: QgsTask, dataset, bbox, timestamp, options):
        """Request a list of available files that are within a bounding box and
        have a specified timestamp"""
        params = {}
        if bbox:
            params['bbox'] = ','.join([str(ext) for ext in bbox])
        if timestamp:
            params['datetime'] = timestamp
    
        url = dataset['links']['files']
        items = self.fetch(task, url, params=params)
    
        # Filter list
        fileList = []

        if not items or not isinstance(items, dict) \
                or not 'features' in items:
            task.exception = self.tr('Error when requesting file list - '
                                     'Unexpected API response')
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
                    
                    # # Make a HEAD request to get the precise file size
                    # This make A LOT of calls, use with care
                    # header = self.fetch(task, asset['href'], method='head')
                    # # Check Content-Length header
                    # file['size'] = 0
                    # if header.hasRawHeader(b'Content-Length'):
                    #     file['size'] = int(header.rawHeader(b'Content-Length'))
            
                    fileList.append(file)

        return fileList
    
    def fetch(self, task: QgsTask, url, params=None, header=None, method='get'):
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

        task.log(self.tr('Start request {}').format(callUrl.toString()))
        # Start request
        if method == 'get':
            self.http.get(request)
        elif method == 'head':
            self.http.head(request)
        
        # Check if request was successful
        r = self.http.reply()
        assert r.error() == QNetworkReply.NoError, r.error()
        
        # Process response
        if method == 'get':
            try:
                return json.loads(str(r.content(), 'utf-8'))
            
            except json.JSONDecodeError as e:
                task.exception = str(e)
                return False
        elif method == 'head':
            return r
        else:
            return None
    
    def fetchHeadLegacy(self, task: QgsTask, url):
        try:
            return requests.head(url)
        except requests.exceptions.HTTPError \
               or requests.exceptions.RequestException as e:
            task.log = self.tr('Error when requesting header information: {}').format(e)
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
        
        task.log(self.tr('Start download of {}').format(callUrl.toString()))
        fileFetcher = QgsFileDownloader(callUrl, filePath)
        
        def onCancel():
            task.exception = self.tr('Download of {} was canceled').format(filename)
            return False
        def onError():
            task.exception = self.tr('Error when downloading {}').format(filename)
            return False
        
        # Run file download in separate event loop
        eventLoop = QEventLoop()
        fileFetcher.downloadError.connect(onError)
        fileFetcher.downloadCanceled.connect(onCancel)
        fileFetcher.downloadCompleted.connect(eventLoop.quit)
        eventLoop.exec_(QEventLoop.ExcludeUserInputEvents)
        fileFetcher.downloadCompleted.disconnect(eventLoop.quit)
        
    def tr(self, message, **kwargs):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject."""
        return QCoreApplication.translate(type(self).__name__, message)
    
    def getCustomOptions(self):
        with open(CUSTOM_OPTION_FILE) as json_file:
            return json.load(json_file)
            
