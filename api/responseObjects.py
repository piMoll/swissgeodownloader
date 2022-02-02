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

class Option:
    def __init__(self):
        self.coordsys = []
        self.resolution = []
        self.format = []
        self.timestamp = []
    
    def fill(self, options):
        for key, option in options.items():
            if not option:
                continue
            if key == 'coordsys':
                self.coordsys = option
            elif key == 'resolution':
                self.resolution = option
            elif key == 'format':
                self.format = option
            elif key == 'timestamp':
                self.timestamp = option
    
    def hasMultipleOptions(self):
        return len(self.coordsys) > 1 or len(self.resolution) > 1 \
               or len(self.format) > 1 or len(self.timestamp) > 1
        

class Dataset:
    def __init__(self, name='', filesLink=''):
        self.id = name
        self.filesLink = filesLink
        self.options = Option()
        self.bbox = None
        self.licenseLink = None
        self.selectByBBox = True
        self.isEmpty = None
        self.avgSize = {}
        self.analysed = False
    
    def setOptions(self, options: dict):
        self.options.fill(options)
    
    def isSingleFile(self):
        return not self.selectByBBox and not self.options.hasMultipleOptions()


class File:
    def __init__(self, name, filetype, href, ext):
        self.id = name
        self.type = filetype
        self.href = href
        self.ext = ext
        self.bbox = None
        self.geom = None
        self.options = Option()
        self.path = None
    
    def setOptions(self, options: dict):
        self.options.fill(options)
