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
import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import QUrl, QUrlQuery, QCoreApplication
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsTask, QgsBlockingNetworkRequest

from ..utils.metadataHandler import saveToFile, loadFromFile
from .. import _AVAILABLE_LOCALES


class ApiGeoCat:
    
    BASEURL = 'https://www.geocat.ch/geonetwork/srv/eng/csw'
    XML_NAMESPACES = {'gmd': '{http://www.isotc211.org/2005/gmd}'}
    REQUEST_PARAMS = {
        'service': 'CSW',
        'version': '2.0.2',
        'request': 'GetRecordById',
        'elementSetName': 'summary',
        'outputFormat': 'application/xml',
        'outputSchema': 'http://www.isotc211.org/2005/gmd',
    }
    DATAPATH = {
        'geoadmin': 'datageoadmin_geocat_metadata.json'
    }
    
    def __init__(self, parent, targetApi):
        """Request metadata from geocat.ch, the official geodata metadata
        service for switzerland."""
        self.baseUrl = self.BASEURL
        self.parent = parent
        self.dataPath = self.DATAPATH[targetApi]
        self.presavedMetadata = {}
        self.loadPresavedMetadata()
        
    def getMeta(self, task: QgsTask, datasetId, metadataUrl, locale):
        """ Requests metadata for a dataset Id. Since calling geocat several
        times on each plugin start is very slow, metadata is saved to a file
        and read from there. Only if there is no metadata for a specific
        dataset in the file, geocat.ch is called."""
        
        metadata = {
            'title': '',
            'description': '',
        }

        # Check if metadata has been presaved and return this data
        if datasetId in self.presavedMetadata \
            and locale in self.presavedMetadata[datasetId]:
                return self.presavedMetadata[datasetId][locale]
        
        geocatDsId = self.extractEntryId(metadataUrl)
        if not geocatDsId:
            task.log(self.tr('Error when trying to retrieve metadata - No dataset ID found'))
            return metadata

        # Call geocat API
        rqParams = self.REQUEST_PARAMS
        rqParams['id'] = geocatDsId
        xml = self.fetch(task, self.BASEURL, params=rqParams)
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            task.log(self.tr('Error when trying to retrieve metadata - Response cannot be parsed'))
            return metadata
        
        # Search for title and description in xml
        searchTerms = {
            'title': f"{self.XML_NAMESPACES['gmd']}title",
            'description': f"{self.XML_NAMESPACES['gmd']}abstract",
        }
        
        for mapsTo, serarchTerm in searchTerms.items():
            xmlElements = [elem for elem in root.iter(tag=serarchTerm)]
            for xmlElem in xmlElements:
                localizedStrings = [elem for elem in xmlElem.iter(tag=f"{self.XML_NAMESPACES['gmd']}LocalisedCharacterString")]
                for localizedString in localizedStrings:
                    if localizedString.get('locale') == '#' + locale.upper():
                        metadata[mapsTo] = localizedString.text
                        break
                if metadata[mapsTo]:
                    break
        
        # Save new metadata to file so we dont' have to call the API again
        self.updatePresavedMetadata(metadata, datasetId, locale)

        return metadata
    
    def refreshPresavedMetadata(self, task, datasetId, url):
        """ Request metadata in all languages for a specific dataset."""
        metadata = {}
        for locale in _AVAILABLE_LOCALES:
            gcMetadata = self.getMeta(task, datasetId, url, locale)
            metadata[locale] = {
                'title': gcMetadata['title'],
                'description': gcMetadata['description'],
            }
        return metadata
    
    def loadPresavedMetadata(self):
        """Read presaved metadata from json file."""
        self.presavedMetadata = loadFromFile(self.dataPath)
    
    def updatePresavedMetadata(self, metadata, datasetId=None, locale=None):
        """Update the presaved metadata with a completely new dicitionary or
        only update partially by adding a new dataset."""
        if datasetId and locale:
            # Make a partial update of the data in the file
            if datasetId not in self.presavedMetadata:
                self.presavedMetadata[datasetId] = {locale: metadata}
            else:
                self.presavedMetadata[datasetId][locale] = metadata
            saveToFile(self.presavedMetadata, self.dataPath)
        else:
            # Fully replace the data in the file
            saveToFile(metadata, self.dataPath)

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
        http = QgsBlockingNetworkRequest()
        if method == 'get':
            http.get(request, forceRefresh=True)
        elif method == 'head':
            http.head(request, forceRefresh=True)
        
        # Check if request was successful
        r = http.reply()
        try:
            assert r.error() == QNetworkReply.NoError, r.error()
        except AssertionError:
            # Service is not reachable
            task.exception = self.tr('swisstopo service not reachable or '
                                     'no internet connection')
            # Service returned an error
            if r.content():
                try:
                    errorResp = json.loads(str(r.content(), 'utf-8'))
                except json.JSONDecodeError as e:
                    task.exception = str(e)
                    return False
                if 'code' and 'description' in errorResp:
                    task.exception = (
                        f"{self.tr('swisstopo service returns error')}: "
                        f"{errorResp['code']} - {errorResp['description']}")
            return False
        
        # Process response
        if method == 'get':
            
            return str(r.content(), 'utf-8')

        elif method == 'head':
            return r
        else:
            return False
    
    def tr(self, message, **kwargs):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject."""
        return QCoreApplication.translate(type(self).__name__, message)
    
    @staticmethod
    def extractEntryId(url):
        if '/metadata/' not in url:
            return None
        entryId = url.split('/')[-1]
        if len(entryId) != 36:
            return None
        return entryId

