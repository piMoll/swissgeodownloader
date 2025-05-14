"""
/***************************************************************************
 SwissGeoDownloader
                                 A QGIS plugin
 This plugin lets you comfortably download swiss geo data.
                             -------------------
        begin                : 2021-03-14
        copyright            : (C) 2022 by Patricia Moll
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
import json
import os

import requests
from qgis.PyQt.QtCore import QCoreApplication, QEventLoop, QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest, QgsFileDownloader

from .apiCallerTask import ApiCallerTask

# Translate context for super class
tr = 'ApiInterface'


class ApiInterface:
    def __init__(self, parent, locale='en'):
        self.parent = parent
        self.locale = locale
        self.name = 'Api'
    
    def fetch(self, task: ApiCallerTask, url, params=None, header=None,
              method='get', decoder='json'):
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
        
        task.log(self.tr('Start request {}', tr).format(callUrl.toString()))
        # Start request
        http = QgsBlockingNetworkRequest()
        if method == 'get':
            http.get(request, forceRefresh=True)
        elif method == 'head':
            http.head(request, forceRefresh=True)
        
        # Check if request was successful
        r = http.reply()
        try:
            assert r.error() == QNetworkReply.NetworkError.NoError, r.error()
        except AssertionError:
            # Service is not reachable
            task.exception = self.tr('{} not reachable or no internet '
                                     'connection', tr).format(self.name)
            # Service returned an error
            if r.content():
                try:
                    errorResp = json.loads(str(r.content(), 'utf-8'))
                except json.JSONDecodeError as e:
                    task.exception = str(e)
                    return False
                if 'code' and 'description' in errorResp:
                    task.exception = (
                        self.tr('{} returns error', tr).format(self.name) +
                        f": {errorResp['code']} - {errorResp['description']}")
            return False
        
        # Process response
        if method == 'get':
            if decoder == 'json':
                try:
                    content = str(r.content(), 'utf-8')
                    if content:
                        return json.loads(content)
                    else:
                        return False
                except json.JSONDecodeError as e:
                    task.exception = str(e)
                    return False
            else:  # decoder string
                return str(r.content(), 'utf-8')
        elif method == 'head':
            return r
        else:
            return False
    
    def fetchHeadLegacy(self, task: ApiCallerTask, url):
        try:
            return requests.head(url)
        except requests.exceptions.HTTPError \
               or requests.exceptions.RequestException as e:
            task.log = self.tr('Error when requesting header '
                               'information: {}', tr).format(e)
            return False
    
    def fetchFile(self, task: ApiCallerTask, url, filename, filePath, part,
                  params=None):
        # Prepare url
        callUrl = QUrl(url)
        if params:
            queryParams = QUrlQuery()
            for key, value in params.items():
                queryParams.addQueryItem(key, str(value))
            callUrl.setQuery(queryParams)
        
        task.log(self.tr('Start download of {}', tr).format(callUrl.toString()))
        fileFetcher = QgsFileDownloader(callUrl, filePath)
        
        def onError():
            task.exception = self.tr('Error when downloading {}', tr).format(filename)
            return False
        def onProgress(bytesReceived, bytesTotal):
            if task.isCanceled():
                task.exception = self.tr('Download of {} was canceled', tr).format(
                    filename)
                fileFetcher.cancelDownload()
            else:
                partProgress = 0
                if bytesTotal > 0:
                    partProgress = (part / 100) * (bytesReceived / bytesTotal)
                task.setProgress(task.progress() + partProgress)
        
        # Run file download in separate event loop
        eventLoop = QEventLoop()
        fileFetcher.downloadError.connect(onError)
        fileFetcher.downloadCanceled.connect(eventLoop.quit)
        fileFetcher.downloadCompleted.connect(eventLoop.quit)
        fileFetcher.downloadProgress.connect(onProgress)
        eventLoop.exec(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        fileFetcher.downloadCompleted.disconnect(eventLoop.quit)
    
    def downloadFiles(self, task: ApiCallerTask, fileList, outputDir):
        task.setProgress(0)
        partProgress = 100 / len(fileList)
        
        for file in fileList:
            savePath = os.path.join(outputDir, file.id)
            self.fetchFile(task, file.href, file.id, savePath, partProgress)
            if task.isCanceled():
                return False
            task.setProgress(task.progress() + partProgress)
        return True
    
    def tr(self, message, context=None, **kwargs):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject."""
        if not context:
            context = type(self).__name__
        return QCoreApplication.translate(context, message)
