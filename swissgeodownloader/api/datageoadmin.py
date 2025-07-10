"""
/***************************************************************************
 SwissGeoDownloader
                                 A QGIS plugin
 This plugin lets you comfortably download swiss geo data.
                             -------------------
        begin                : 2021-03-14
        copyright            : (C) 2025 by Patricia Moll
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
from copy import deepcopy

from qgis.core import Qgis

from swissgeodownloader.api.apiCallerTask import ApiCallerTask
from swissgeodownloader.api.apiInterface import ApiInterface
from swissgeodownloader.api.geocat import ApiGeoCat
from swissgeodownloader.api.responseObjects import (Asset, CURRENT_VALUE,
                                                    Collection, FILETYPE_COG)
from swissgeodownloader.utils.filterUtils import (cleanupFilterItems,
                                                  currentFileByBbox)
from .. import _AVAILABLE_LOCALES

BASEURL = 'https://data.geo.admin.ch/api/stac/v1/collections'
API_EPSG = 'EPSG:4326'
OPTION_MAPPER = {
    'filetype': 'type',
    'category': 'geoadmin:variant',
    'resolution': 'gsd',
    'timestamp': 'datetime',
    'coordsys': 'proj:epsg',
    }
API_OPTION_MAPPER = {y: x for x, y in OPTION_MAPPER.items()}
API_METADATA_URL = 'https://api3.geo.admin.ch/rest/services/api/MapServer'
FETCH_ALL_LIMIT = 500


class ApiDataGeoAdmin(ApiInterface):
    
    def __init__(self, parent, locale='en'):
        super().__init__(parent, locale)
        self.name = 'Swisstopo API'
        self.geocatApi = ApiGeoCat(parent, locale, 'geoadmin')
    
    def getCollections(self, task: ApiCallerTask):
        """Get a list of all available collections and read out title,
        description and other properties."""
        # Request collections list
        response = self.fetchAll(task, BASEURL, 'collections')
        if response is False:
            if not task.exception:
                task.exception = self.tr('Error when loading available dataset'
                                         ' - Unexpected API response')
            return False
        
        # Geoadmin metadata: Fetches translated titles and descriptions
        #  of collections
        md_geoadmin = self.getMetadata(task)
        
        collections = self.processCollections(response, md_geoadmin, task)
        # For all collections that lack metadata (e.g. title) add external
        #  metadata from geocat
        return self.addExternalMetadata(collections, self.geocatApi,
                                        self.locale, task)
    
    @staticmethod
    def processCollections(collections, metadata, task: ApiCallerTask):
        collectionList = {}
        for col in collections:
            
            if task.isCanceled():
                return False
            
            collection = Collection(col['id'],
                                    [link['href'] for link in col['links']
                              if link['rel'] == 'items'][0])
            collection.title = col['title']
            try:
                collection.description = col['description']
            except (KeyError, IndexError):
                task.log(f"No description available for '{collection.title}'",
                         debugMsg=True)
            try:
                collection.bbox = col['extent']['spatial']['bbox'][0]
            except (KeyError, IndexError):
                task.log(f"No bbox available for '{collection.title}'",
                         debugMsg=True)
            try:
                collection.licenseLink = [link['href'] for link in col['links']
                                       if link['rel'] == 'license'][0]
            except (KeyError, IndexError):
                task.log(f"No licence link available for '{collection.title}'",
                         debugMsg=True)
            try:
                collection.metadataLink = \
                    [link['href'] for link in col['links']
                                       if link['rel'] == 'describedby'][0]
            except (KeyError, IndexError):
                task.log(
                        f"No metadata link available for '{collection.title}'",
                        debugMsg=True)
            
            # Add metadata in the correct language from geocat API
            if collection.id in metadata:
                # Get the pre-saved metadata from the json file
                collection.title = metadata[collection.id].get('title')
                collection.description = metadata[collection.id].get(
                    'description')
            
            collectionList[collection.id] = collection
        
        return collectionList
    
    @staticmethod
    def addExternalMetadata(collections, metadataService, locale,
                            task: ApiCallerTask):
        for col in collections:
            if task.isCanceled():
                return False
            if col.title:
                continue
            # Get metadata from geocat.ch
            metadata = metadataService.getMeta(task, col.id,
                                               col.metadataLink, locale)
            if not metadata:
                continue
            
            col.title = metadata.get('title')
            col.description = metadata.get('description')
            # Save metadata to file so we don't have to call the API again
            metadataService.updatePreSavedMetadata(metadata, col.id,
                                                   locale)
        return collections
    
    def getMetadata(self, task: ApiCallerTask):
        """ Calls geoadmin API and retrieves translated titles and
        descriptions."""
        metadata = {}
        
        params = {
            'lang': self.locale
            }
        faqData = self.fetch(task, API_METADATA_URL, params)
        if not faqData or not isinstance(faqData, dict) \
                or 'layers' not in faqData:
            return metadata
        
        for layer in faqData['layers']:
            if task.isCanceled():
                return False
            
            title = ''
            description = ''
            if 'layerBodId' not in layer:
                continue
            layerId = layer['layerBodId']
            if 'fullName' in layer:
                title = layer['fullName']
            if 'attributes' in layer and 'inspireAbstract' in layer['attributes']:
                description = layer['attributes']['inspireAbstract']
            
            metadata[layerId] = {
                'title': title,
                'description': description
                }
        return metadata
    
    def getCollectionDetails(self, task: ApiCallerTask, collection):
        """Analyse collection to figure out available options in gui"""
        url = collection.filesLink
        # Get max. 40 features
        items = self.fetch(task, url, params={'limit': 40})
    
        if not items or not isinstance(items, dict) \
                or 'features' not in items:
            if not task.exception:
                task.exception = self.tr('Error when loading dataset details '
                                         '- Unexpected API response')
            return False
        
        estimate = {}
        fileCount = len(items['features'])
        
        # Check if it makes sense to select by bbox or if the full file list
        #  should just be downloaded directly
        if fileCount <= 10:
            collection.selectByBBox = False
        
        # Analyze size of an item to estimate download sizes later on
        if fileCount > 0:
            item = items['features'][-1]
            
            # Get an estimate of file size
            for assetId in item['assets']:
                if task.isCanceled():
                    return False
                
                asset = item['assets'][assetId]
                # Don't request again if we have this estimate already
                if asset['type'] in estimate.keys():
                    continue
                # Check Content-Length header: Make a HEAD request to get the file size
                header = self.fetch(task, asset['href'], method='head')
                if header and header.hasRawHeader(b'Content-Length'):
                    estimate[asset['type']] = int(
                            header.rawHeader(b'Content-Length'))
        
        collection.analysed = True
        collection.isEmpty = fileCount == 0
        collection.avgSize = estimate
        return collection
    
    def getFileList(self, task: ApiCallerTask, url, bbox: list[float] or None):
        """Request a list of available files that are within a bounding box.
        Analyse the received list and extract file properties."""
        params = {}
        if bbox:
            params['bbox'] = ','.join([str(ext) for ext in bbox])

        # Request files
        responseList = self.fetchAll(task, url, 'features', params=params,
                                     limit=FETCH_ALL_LIMIT)
        if responseList is False:
            if not task.exception:
                task.exception = self.tr('Error when requesting file list - '
                                         'Unexpected API response')
            return False
        return self.processItems(responseList, task)
    
    @staticmethod
    def processItems(responseList, task: ApiCallerTask):
        filterItems = {
            'filetype': [],
            'category': [],
            'resolution': [],
            'timestamp': [],
            'coordsys': [],
            }
        fileList = []
            
        for item in responseList:
            if task.isCanceled():
                return False
            
            # Readout timestamp from the item itself
            try:
                timestamp = item['properties'][OPTION_MAPPER['timestamp']]
                endTimestamp = None
            except KeyError:
                # Try to get timestamp from 'start_datetime' and 'end_datetime'
                timestamp = item['properties'].get('start_datetime')
                endTimestamp = item['properties'].get('end_datetime')
                if not timestamp:
                    # Extract the mandatory timestamp 'created' instead
                    timestamp = item['properties']['created']
            
            # Save all files and their properties
            for assetId in item['assets']:
                if task.isCanceled():
                    return False
                
                asset = item['assets'][assetId]
                
                # Create file object
                file = Asset(assetId, asset['type'], asset['href'])
                try:
                    file.setBbox(item['bbox'])
                except AssertionError as e:
                    task.log((f"File {file.id}: Bounding box not valid:"
                              f" {e} {item['bbox']}"),
                             Qgis.MessageLevel.Warning)
                
                file.geom = item['geometry']
                
                # Extract file properties, save them to the file object
                #  and add them to the filter list
                
                fileWithMultipleTypes = []
                if OPTION_MAPPER['filetype'] in asset:
                    completeFiletype = str(asset[OPTION_MAPPER['filetype']])
                    filetype = completeFiletype.split(';')[0]
                    if '/' in filetype:
                        filetype = filetype.split('/')[1]
                    if filetype.startswith('x.'):
                        filetype = filetype[2:]
                    file.filetype = filetype
                    fileWithMultipleTypes.append(filetype)
                    if completeFiletype == 'image/tiff; application=geotiff; profile=cloud-optimized':
                        fileWithMultipleTypes.append(FILETYPE_COG)
                    filterItems['filetype'].extend(fileWithMultipleTypes)
                
                if OPTION_MAPPER['category'] in asset:
                    file.category = str(asset[OPTION_MAPPER['category']])
                    filterItems['category'].append(file.category)
                    
                if OPTION_MAPPER['resolution'] in asset:
                    file.resolution = str(asset[OPTION_MAPPER['resolution']])
                    filterItems['resolution'].append(file.resolution)
                    
                if timestamp:
                    try:
                        file.setTimestamp(timestamp, endTimestamp)
                    except ValueError:
                        task.log(f"File {file.id}: Timestamp not valid)", Qgis.MessageLevel.Warning)
                    filterItems['timestamp'].append(file.timestampStr)
                    
                if OPTION_MAPPER['coordsys'] in asset:
                    file.coordsys = str(asset[OPTION_MAPPER['coordsys']])
                    filterItems['coordsys'].append(file.coordsys)
                
                fileList.append(file)
                # If one asset can support multiple file types (e.g. tif and
                #  COG), create a copy of the file for each file type
                if len(fileWithMultipleTypes) > 1:
                    for fileType in fileWithMultipleTypes[1:]:
                        copiedFile = deepcopy(file)
                        copiedFile.filetype = fileType
                        fileList.append(copiedFile)

        # Sort file list by bbox coordinates (first item on top left corner)
        fileList.sort(key=lambda f: round(f.bbox[3], 2) if f.bbox else 0,
                      reverse=True)
        fileList.sort(key=lambda f: round(f.bbox[0], 2) if f.bbox else 0)
        
        # Clean up filter items by removing duplicates and adding an 'ALL' entry
        filterItems = cleanupFilterItems(filterItems)
        
        # Extract most current file (timestamp) for every bbox on the map
        if len(filterItems['timestamp']) >= 2:
            mostCurrentFileInBbox = currentFileByBbox(fileList)
                
            if len(mostCurrentFileInBbox.keys()) > 1:
                for savedBboxDicts in mostCurrentFileInBbox.values():
                    for file in savedBboxDicts.values():
                        file.isMostCurrent = True
                filterItems['timestamp'].insert(0, CURRENT_VALUE)
        
        return {'files': fileList, 'filters': filterItems}
    
    def refreshAllMetadata(self, task: ApiCallerTask):
        """Fetches metadata for all collections and saves it to a json file."""
        collections = self.getCollections(task)
        
        md_geocat = {}
        for collectionId, collection in collections.items():
            # Request metadata in all languages
            metadata = {}
            for locale in _AVAILABLE_LOCALES:
                localizedMetadata = self.geocatApi.getMeta(task, collectionId,
                                                           collection.metadataLink,
                                                           locale)
                if localizedMetadata:
                    metadata[locale] = localizedMetadata
            md_geocat[collectionId] = metadata
        
        self.geocatApi.updatePreSavedMetadata(md_geocat)
    
    def catalogPropertiesCrawler(self, task: ApiCallerTask):
        """Crawls through all item / asset properties of the catalog and
        returns them."""
        collections = self.getCollections(task)
        items = {}
        for collectionId, collection in collections.items():
            items[collectionId] = {}
            items[collectionId]['title'] = collection.title
            bbox = [7.8693964, 46.7961371, 7.9098771, 46.817595]
            fileList = self.getFileList(task, collection.filesLink, bbox)
            if fileList:
                items[collectionId]['assets'] = len(fileList['files'])
                items[collectionId]['filters'] = {
                    k: v for k, v in fileList['filters'].items() if v}
        return items
