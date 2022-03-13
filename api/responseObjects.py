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

ALL_VALUE = 'all'
CURRENT_VALUE = 'current'

class Dataset:
    def __init__(self, name='', filesLink=''):
        self.id = name
        self.filesLink = filesLink
        self.isSingleFile = False
        self.bbox = None
        self.licenseLink = None
        self.selectByBBox = True
        self.isEmpty = None
        self.avgSize = {}
        self.analysed = False


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
        self.coordsys = None

        self.isMostCurrent = False
    
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
                or (filterValue and self.timestamp == filterValue)
                or (self.timestamp is None)
                or (filterValue == ALL_VALUE)
                or (filterValue == CURRENT_VALUE and self.isMostCurrent))

    def coordsysFitsFilter(self, filterValue):
        return (not filterValue
                or (filterValue and self.coordsys == filterValue)
                or (self.coordsys is None)
                or (filterValue == ALL_VALUE))
