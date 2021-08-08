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

from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsRubberBand
from qgis.core import QgsRectangle, QgsGeometry, QgsWkbTypes
from .qgis_utilities import transformBbox


class BboxDrawer:
    
    COLOR_SELECT = QColor(171, 0, 12, 30)
    COLOR_UNSELECT = QColor(171, 171, 171, 30)
    COLOR_BORDER =  QColor(171, 0, 12)
    WIDTH_BORDER = 3
    
    def __init__(self, canvas, transformer):
        self.canvas = canvas
        self.transformer = transformer
        self.bboxItems = {}
    
    def addBboxes(self, fileList):
        self.removeAll()
        for file in fileList.values():
            if not file.bbox and not sum(file.bbox) > 0:
                continue
            coordinates = transformBbox(QgsRectangle(*tuple(file.bbox)),
                                        self.transformer)
            rectangle = QgsRectangle(*tuple(coordinates))
            polygon = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            polygon.setToGeometry(QgsGeometry().fromRect(rectangle))
            polygon.setColor(self.COLOR_BORDER)
            polygon.setFillColor(self.COLOR_SELECT)
            polygon.setWidth(self.WIDTH_BORDER)
            polygon.show()
            self.bboxItems[file.id] = { 'polygon': polygon, 'selected': True}
    
    def removeAll(self):
        for item in self.bboxItems.values():
            item['polygon'].reset()
            del item['polygon']
        self.bboxItems = {}
        
    def switchState(self, fileId):
        # TODO: Check first: is clicking possible without moving the map?
        #  1. get coordinates, select right rectangle, change color of rectangle
        #  2. return name of file corresponding to rectangle
        #  3. deselect file in file list
        if fileId in self.bboxItems:
            item = self.bboxItems[fileId]
            if item['selected']:
                item['polygon'].setFillColor(self.COLOR_UNSELECT)
            else:
                item['polygon'].setFillColor(self.COLOR_SELECT)
            item['selected'] = not item['selected']
   
    def updateRefSystem(self, newTransformer):
        self.transformer = newTransformer
        for item in self.bboxItems.values():
            geom = item['polygon'].getGeometry() # TODO
            rectangle = geom.toRctangle() # TODO
            coordinates = transformBbox(rectangle, self.transformer)
            rectangle = QgsRectangle(*tuple(coordinates))

            item['polygon'].reset()
            item['polygon'].setToGeometry(QgsGeometry().fromRect(rectangle))
