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

from .apiCallerTask import ApiCallerTask
from .apiInterface import ApiInterface
from .geocat import ApiGeoCat
from .responseObjects import (CURRENT_VALUE, Dataset, FILETYPE_COG, File)
from ..utils.filterUtils import cleanupFilterItems, currentFileByBbox

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


class ApiDataGeoAdmin(ApiInterface):
    
    def __init__(self, parent, locale='en'):
        super().__init__(parent, locale)
        self.name = 'Swisstopo API'
        self.geocatApi = ApiGeoCat(parent, locale, 'geoadmin')
    
    def getDatasetList(self, task: ApiCallerTask, refreshMetadata=False):
        """Get a list of all available datasets and read out title,
        description and other properties."""
        # Request dataset list
        collection = self.fetchAll(task, BASEURL, 'collections')
        if collection is False:
            if not task.exception:
                task.exception = self.tr('Error when loading available dataset'
                                         ' - Unexpected API response')
            return False
        
        datasetList = {}
        # Geoadmin metadata: Fetches translated titles and descriptions
        #  of datasets
        md_geoadmin = self.getMetadata(task)
        # Geocat metadata: Alternative if geoadmin does not have the dataset
        md_geocat = {}
        
        for ds in collection:
            
            if task.isCanceled():
                return False

            dataset = Dataset(ds['id'], [link['href'] for link in ds['links']
                              if link['rel'] == 'items'][0])
            dataset.title = ds['title']
            try:
                dataset.description = ds['description']
            except (KeyError, IndexError):
                task.log(f"No description available for '{dataset.title}'", debugMsg=True)
            try:
                dataset.bbox = ds['extent']['spatial']['bbox'][0]
            except (KeyError, IndexError):
                task.log(f"No bbox available for '{dataset.title}'", debugMsg=True)
            try:
                dataset.licenseLink = [link['href'] for link in ds['links']
                                       if link['rel'] == 'license'][0]
            except (KeyError, IndexError):
                task.log(f"No licence link available for '{dataset.title}'", debugMsg=True)
            try:
                dataset.metadataLink = [link['href'] for link in ds['links']
                                       if link['rel'] == 'describedby'][0]
            except (KeyError, IndexError):
                task.log(f"No metadata link available for '{dataset.title}'", debugMsg=True)
            
            # Add metadata in the correct language from geocat API
            if dataset.id in md_geoadmin:
                # Get the pre-saved metadata from the json file
                dataset.title = md_geoadmin[dataset.id].get('title')
                dataset.description = md_geoadmin[dataset.id].get(
                    'description')
            if not dataset.title:
                # Get metadata from geocat.ch: This will save the metadata to
                #  a file so it does not have to be requested every time
                metadata = self.geocatApi.getMeta(task, dataset.id,
                                                  dataset.metadataLink,
                                                  self.locale)
                if metadata:
                    dataset.title = metadata.get('title')
                    dataset.description = metadata.get('description')
                    # Save metadata to file so we don't have to call the API again
                    self.geocatApi.updatePreSavedMetadata(metadata, dataset.id,
                                                          self.locale)
            
            if refreshMetadata:
                # Request metadata in all languages. This is only used
                #  when we want to refresh the local geocat metadata file.
                md_geocat[dataset.id] = self.geocatApi.getMetadataInAllLocales(
                    task, dataset.id, dataset.metadataLink)

            datasetList[dataset.id] = dataset

        if refreshMetadata:
            self.geocatApi.updatePreSavedMetadata(md_geocat)
        
        return datasetList
    
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
            title = ''
            description = ''
            if not 'layerBodId' in layer:
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
    
    def getDatasetDetails(self, task: ApiCallerTask, dataset):
        """Analyse dataset to figure out available options in gui"""
        url = dataset.filesLink
        # Get max. 40 features
        items = self.fetch(task, url, params={'limit' : 40})
    
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
                if Qgis.QGIS_VERSION_INT >= 31800:
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
    
    def getFileList(self, task: ApiCallerTask, url, bbox):
        """Request a list of available files that are within a bounding box.
        Analyse the received list and extract file properties."""
        params = {}
        if bbox:
            params['bbox'] = ','.join([str(ext) for ext in bbox])

        # Request files
        responseList = self.fetchAll(task, url, 'features', params=params)
        if responseList is False:
            if not task.exception:
                task.exception = self.tr('Error when requesting file list - '
                                         'Unexpected API response')
            return False
        
        filterItems = {
            'filetype': [],
            'category': [],
            'resolution': [],
            'timestamp': [],
            'coordsys': [],
        }
        fileList = []
            
        for item in responseList:
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
                asset = item['assets'][assetId]
                
                # Create file object
                file = File(assetId, asset['type'], asset['href'])
                try:
                    file.setBbox(item['bbox'])
                except AssertionError:
                    task.log(f"File {file.id}: Bounding box not valid", Qgis.MessageLevel.Warning)
                    
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
        fileList.sort(key=lambda f: round(f.bbox[3], 2), reverse=True)
        fileList.sort(key=lambda f: round(f.bbox[0], 2))
        
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
    
    def fetchAll(self, task: ApiCallerTask, url, responsePropName, params=None,
                 header=None, method='get'):
        responseList = []
    
        # Fetch more responses as long as there is a 'next' link
        #  in the response
        while url:
            if task.isCanceled():
                return False
        
            response = self.fetch(task, url, params, header, method)
        
            if not response or not isinstance(response, dict) \
                    or not responsePropName in response:
                return False
        
            responseList.extend(response[responsePropName])
        
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
        return responseList
