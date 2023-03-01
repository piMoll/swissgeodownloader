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
from ..ui.ui_utilities import getDateFromIsoString

ALL_VALUE = 'all'
CURRENT_VALUE = 'current'
P_SIMILAR = 0.20    # max 20% difference


class Dataset:
    def __init__(self, ident='', filesLink=''):
        self.id = ident
        self.filesLink = filesLink
        self.title = None
        self.description = None
        self.bbox = None
        self.licenseLink = None
        self.metadataLink = None
        self.selectByBBox = True
        self.isEmpty = None
        self.avgSize = {}
        self.analysed = False

    @property
    def searchtext(self):
        return ' '.join([self.id or '', self.title or '', self.description or ''])\
                    .replace('.', ' ').lower()


class File:
    def __init__(self, name, filetype, href):
        self.id = name
        self.type = filetype
        self.href = href
        self.bbox = None
        self.geom = None
        self.path = None
        
        self.filetype = None
        self.format = None
        self.resolution = None
        self.timestamp = None
        self.timestampStr = ''
        self.coordsys = None

        self.isMostCurrent = False

    @property
    def bboxKey(self):
        if not self.bbox:
            return ''
        # This will round the coordinates to ~ 5-10 m
        return '|'.join([str(round(coord, 4)) for coord in self.bbox])

    @property
    def propKey(self):
        propList = [self.filetype, self.format, self.resolution]
        return '|'.join([elem for elem in propList if elem is not None])
    
    def setBbox(self, bbox):
        # Bbox entries should be numbers and inside coordinate ranges of WGS84
        try:
            assert isinstance(bbox, list)
            assert len(bbox) == 4
            assert [isinstance(c, float) or isinstance(c, int) for c in bbox]
            assert -180 <= bbox[0] <= 180 and -180 <= bbox[2] <= 180
            assert -90 <= bbox[1] <= 90 and -90 <= bbox[3] <= 90
        except AssertionError as e:
            self.bbox = None
            raise e
        
        self.bbox = bbox

    def setTimestamp(self, timestamp):
        try:
            self.timestamp = getDateFromIsoString(timestamp, False)
            self.timestampStr = getDateFromIsoString(timestamp)
        except ValueError as e:
            self.timestamp = None
            self.timestampStr = ''
            raise e
    
    def filetypeFitsFilter(self, filterValue):
        return (not filterValue
                or (filterValue and self.filetype == filterValue)
                or (self.filetype is None)
                or (filterValue == ALL_VALUE))
    
    def formatFitsFilter(self, filterValue):
        return (not filterValue
                or (filterValue and self.format == filterValue)
                or (self.format is None)
                or (filterValue == ALL_VALUE))
    
    def resolutionFitsFilter(self, filterValue):
        return (not filterValue
                or (filterValue and self.resolution == filterValue)
                or (self.resolution is None)
                or (filterValue == ALL_VALUE))

    def timestampFitsFilter(self, filterValue):
        return (not filterValue
                or (filterValue and self.timestampStr == filterValue)
                or (self.timestampStr is None)
                or (filterValue == ALL_VALUE)
                or (filterValue == CURRENT_VALUE and self.isMostCurrent))

    def coordsysFitsFilter(self, filterValue):
        return (not filterValue
                or (filterValue and self.coordsys == filterValue)
                or (self.coordsys is None)
                or (filterValue == ALL_VALUE))

    def hasSimilarBboxAs(self, bbox):
        if not self.bbox or not bbox:
            return False
        
        try:
            # bbox pattern: E1, N1, E2, N2 (e.g. 5°, 45°, 7°, 47°)
            height = bbox[3] - bbox[1]
            s_height = self.bbox[3] - self.bbox[1]
            length = bbox[2] - bbox[0]
            s_length = self.bbox[2] - self.bbox[0]
            
            assert s_height != 0 and s_length != 0
            
            # Check if similar bbox length
            assert (1 - P_SIMILAR) < abs((length) / (s_length)) < (1 + P_SIMILAR)
            # Check if similar bbox height
            assert (1 - P_SIMILAR) < abs((height) / (s_height)) < (1 + P_SIMILAR)
            
            # Check if similar absolute position of corner points
            assert abs(self.bbox[0] - bbox[0]) < s_length * P_SIMILAR
            assert abs(self.bbox[1] - bbox[1]) < s_height * P_SIMILAR
            assert abs(self.bbox[2] - bbox[2]) < s_length * P_SIMILAR
            assert abs(self.bbox[3] - bbox[3]) < s_height * P_SIMILAR
        
        except AssertionError:
            return False
        
        return True
