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
import json
import requests

from qgis.PyQt.QtCore import QEventLoop, QUrl, QUrlQuery, QCoreApplication
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import (QgsTask, QgsFileDownloader, QgsBlockingNetworkRequest,
                       Qgis)
from .responseObjects import Dataset, File
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
    
    def getDatasetList(self, task: QgsTask):
        """Get a list of all available datasets and read out with options the
        dataset supports"""
        collection = self.fetch(task, self.baseUrl)
        
        if not collection or not isinstance(collection, dict) \
                or 'collections' not in collection:
            if not task.exception:
                task.exception = self.tr('Error when loading available dataset - '
                                         'Unexpected API response')
            return False

        # Read out custom overwrites for dataset options from a config file
        overwriteRules = self.getCustomOptions()
        
        datasetList = {}
        for ds in collection['collections']:
            
            if task.isCanceled():
                return False

            # Check if there are overwrites for this dataset
            overwrite = None
            if ds['id'] in overwriteRules:
                overwrite = overwriteRules[ds['id']]
                
            # Skip this dataset
            if overwrite and 'ignore' in overwrite:
                continue
            
            dataset = Dataset(ds['id'], [link['href'] for link in ds['links']
                              if link['rel'] == 'items'][0])
            dataset.bbox = ds['extent']['spatial']['bbox'][0]
            dataset.licenseLink = [link['href'] for link in ds['links']
                                   if link['rel'] == 'license'][0]
            
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
                    if (overwrite and 'options' in overwrite
                        and 'timestamp' in overwrite['options']
                        and overwrite['options']['timestamp'] == 'first'):
                        options['timestamp'] = [options['timestamp'][0]]

            dataset.setOptions(options)
            datasetList[dataset.id] = dataset
        
        return datasetList
    
    def getDatasetDetails(self, task: QgsTask, dataset):
        """Analyse dataset to figure out available options in gui"""
        url = dataset.filesLink
        # Get max. 40 features
        items = self.fetch(task, url, params={'limit' : 40})

        fileCount = 0
        estimate = {}
        
        if items and isinstance(items, dict) and 'features' in items:
            fileCount = len(items['features'])
            
            # Check if it makes sense to select by bbox
            # TODO: this should also check options and see, if there is only
            #  one file per option (e.g. farbe-pk100)
            if fileCount <= 1 or (dataset.options.timestamp
                and fileCount == len(dataset.options.timestamp)):
                dataset.selectByBBox = False
            
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

        dataset.analysed = True
        dataset.isEmpty = fileCount == 0
        dataset.avgSize = estimate
        return dataset

    def getFileList(self, task: QgsTask, url, bbox, timestamp, options):
        """Request a list of available files that are within a bounding box and
        have a specified timestamp"""
        params = {}
        if bbox:
            params['bbox'] = ','.join([str(ext) for ext in bbox])
        if timestamp:
            params['datetime'] = timestamp
        
        # Response and filtered list of files
        responseList = []
        fileList = []

        # Fetch more responses as long as there is a 'next' link
        #  in the response
        while url:
            if task.isCanceled():
                break
            
            response = self.fetch(task, url, params=params)
        
            if not response or not isinstance(response, dict) \
                    or not 'features' in response:
                task.exception = self.tr('Error when requesting file list - '
                                         'Unexpected API response')
                return False
            
            responseList.extend(response['features'])
            
            # Get the next bunch of files by using the next link
            #  in the response
            nextUrl = ''
            if response['links']:
                for link in response['links']:
                    if link['rel'] == 'next':
                        nextUrl = link['href']
                        break
            if url != nextUrl:
                url = nextUrl
                # Params are already part of the next url, no need to
                #  specify them again
                params = {}
            else:
                url = ''
            
        for item in responseList:
            # Filter assets so that we only get the one file that matches the
            #  defined options
            for assetId in item['assets']:
                if task.isCanceled():
                    return False
        
                asset = item['assets'][assetId]
        
                # Filter out all files that match the specified options
                optionsMatch = []
                for optionName, optionValue in options.items():
                    optionApiName = OPTION_MAPPER[optionName]
            
                    optionsMatch.append(optionApiName in asset.keys() and
                                        optionValue == asset[
                                            optionApiName])
        
                if sum(optionsMatch) == len(optionsMatch):
                    # Analyse file extension
                    filename = os.path.splitext(assetId)[0]
                    ext = os.path.splitext(assetId)[1]
                    ext2 = ''
                    # If file is a zip, look at the filename again and get
                    #  file type inside zip
                    if ext == '.zip' and len(os.path.splitext(filename)[1]) == 4:
                        ext2 = os.path.splitext(filename)[1]
                    
                    # Create file object
                    file = File(assetId, asset['type'], asset['href'],
                                ext2 + ext)
                    file.setOptions(options)
                    file.bbox = item['bbox']
                    file.geom = item['geometry']
                    
                    # # Make a HEAD request to get the precise file size
                    # This make A LOT of calls, use with care
                    # header = self.fetch(task, asset['href'], method='head')
                    # # Check Content-Length header
                    # file['size'] = 0
                    # if header.hasRawHeader(b'Content-Length'):
                    #     file['size'] = int(header.rawHeader(b'Content-Length'))
                    
                    fileList.append(file)

        # Sort file list by bbox coordinates (first item on top left corner)
        fileList.sort(key=lambda f: round(f.bbox[3], 2), reverse=True)
        fileList.sort(key=lambda f: round(f.bbox[0], 2))
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
        try:
            assert r.error() == QNetworkReply.NoError, r.error()
        except AssertionError:
            task.exception = self.tr('swisstopo service not reachable or '
                                     'no internet connection')
            return False
        
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
            return False
    
    def fetchHeadLegacy(self, task: QgsTask, url):
        try:
            return requests.head(url)
        except requests.exceptions.HTTPError \
               or requests.exceptions.RequestException as e:
            task.log = self.tr('Error when requesting header information: {}').format(e)
            return False

    def downloadFiles(self, task: QgsTask, fileList, outputDir):
        task.setProgress(0)
        partProgress = 100 / len(fileList)
        
        for file in fileList:
            savePath = os.path.join(outputDir, file.id)
            self.fetchFile(task, file.href, file.id, savePath, partProgress)
            if task.isCanceled():
                return False
            task.setProgress(task.progress() + partProgress)
        return True
    
    def fetchFile(self, task: QgsTask, url, filename, filePath, part, params=None):
        # Prepare url
        callUrl = QUrl(url)
        if params:
            queryParams = QUrlQuery()
            for key, value in params.items():
                queryParams.addQueryItem(key, str(value))
            callUrl.setQuery(queryParams)
        
        task.log(self.tr('Start download of {}').format(callUrl.toString()))
        fileFetcher = QgsFileDownloader(callUrl, filePath)
        
        def onError():
            task.exception = self.tr('Error when downloading {}').format(filename)
            return False
        def onProgress(bytesReceived, bytesTotal):
            if task.isCanceled():
                task.exception = self.tr('Download of {} was canceled').format(
                    filename)
                fileFetcher.cancelDownload()
            else:
                partProgress = (part / 100) * (bytesReceived / bytesTotal)
                task.setProgress(task.progress() + partProgress)
        
        # Run file download in separate event loop
        eventLoop = QEventLoop()
        fileFetcher.downloadError.connect(onError)
        fileFetcher.downloadCanceled.connect(eventLoop.quit)
        fileFetcher.downloadCompleted.connect(eventLoop.quit)
        fileFetcher.downloadProgress.connect(onProgress)
        eventLoop.exec_(QEventLoop.ExcludeUserInputEvents)
        fileFetcher.downloadCompleted.disconnect(eventLoop.quit)
        
    def tr(self, message, **kwargs):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject."""
        return QCoreApplication.translate(type(self).__name__, message)
    
    def getCustomOptions(self):
        with open(CUSTOM_OPTION_FILE) as json_file:
            return json.load(json_file)
            
