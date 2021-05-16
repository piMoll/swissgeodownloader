import os
import requests
import json

from PyQt5.QtCore import QEventLoop, QUrl
from PyQt5.QtNetwork import QNetworkReply
from qgis.core import QgsTask, QgsNetworkContentFetcher
from .api_datageoadmin import getMetaData

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
            
            # Check if files can be selected by specifying bbox or if the
            #  dataset contains only one file
            useBBox = True
            fileCount = getMetaData(dataset)
            if fileCount <= 1 or ('timestamp' in options
                                  and fileCount == len(options['timestamp'])):
                useBBox = False
            dataset['selectByBBox'] = useBBox
            
            datasetList[dataset['id']] = dataset
        
        return datasetList
    
    def fetch(self, url, task):
        self.fetcher.fetchContent(QUrl(url))
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
        
        

