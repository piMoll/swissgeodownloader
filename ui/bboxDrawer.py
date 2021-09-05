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

from qgis.PyQt.QtGui import QColor, QTextDocument
from qgis.PyQt.QtCore import QSizeF, QPointF
from qgis.gui import QgsRubberBand
from qgis.core import (QgsRectangle, QgsGeometry, QgsWkbTypes, QgsPointXY,
                       QgsTextAnnotation, QgsAnnotationManager,
                       QgsCoordinateTransform)
from .qgis_utilities import transformBbox


class BboxPainter:
    """Paints the bounding boxes of the listed file into the map and labels
    them with their row number."""
    
    MAX_VISIBLE_SCALE = 100000
    MAX_BBOX_TO_DISPLAY = 8000
    
    def __init__(self, canvas, transformer: QgsCoordinateTransform,
                 annotationManager: QgsAnnotationManager):
        self.canvas = canvas
        self.transformer = transformer
        self.annotationManager = annotationManager
        self.bboxItems = {}
        self.numberIsVisible = True
    
    def paintBoxes(self, fileList, mapScale):
        self.removeAll()
        # Limit max items to show in the map
        if len(fileList.values()) > self.MAX_BBOX_TO_DISPLAY:
            return
        for idx, file in enumerate(fileList.values()):
            if not file.bbox and not sum(file.bbox) > 0:
                continue
            coordinates = transformBbox(QgsRectangle(*tuple(file.bbox)),
                                        self.transformer)
            rectangle = QgsRectangle(*tuple(coordinates))
            # Bbox shape
            bbox = BboxMapItem(self.canvas, rectangle, file.id)
            self.bboxItems[file.id] = bbox
            
            # Row number as annotation
            html = ('<div style="font-size: 20px; color: rgb(0,102,255); '
                    'text-align: center; background-color: rgba(255,255,255)">'
                    '<strong>' + str(idx+1) + '</strong></div>')
            a = QgsTextAnnotation()
            c = QTextDocument()
            c.setHtml(html)
            a.setDocument(c)
            a.setMarkerSymbol(None)
            a.setFillSymbol(None)
            labelPos = QgsPointXY(rectangle.center())
            a.setMapPosition(labelPos)
            numberLen = len(str(idx+1))-1
            # Dimensions for white background box depending on number length
            sizes = [[6, 3], [9, 4], [12, 6]]
            a.setFrameSizeMm(QSizeF(sizes[numberLen][0], 14))
            a.setFrameOffsetFromReferencePointMm(QPointF(-sizes[numberLen][1], -4))
            a.setMapPositionCrs(self.transformer.destinationCrs())
            # Add annotation to annotation manager so it can be removed
            self.annotationManager.addAnnotation(a)
        self.switchNumberVisibility(mapScale)
    
    def switchNumberVisibility(self, mapScale):
        # Check if annotation numbering should be visible
        isVisible = round(mapScale) <= self.MAX_VISIBLE_SCALE
        if self.numberIsVisible != isVisible:
            self.numberIsVisible = isVisible
            # Switch visibility of all annotations
            for ann in self.annotationManager.annotations():
                ann.setVisible(self.numberIsVisible)
    
    def removeAll(self):
        for item in self.bboxItems.values():
            item.reset()
            del item
        self.bboxItems = {}
        for ann in self.annotationManager.annotations():
            self.annotationManager.removeAnnotation(ann)
        self.numberIsVisible = True
    
    def switchSelectState(self, fileId):
        bbox = self.bboxItems[fileId]
        bbox.switchSelected()


class BboxMapItem(QgsRubberBand):
    """Creates a rectangle from a QgsRubberBand in the map."""
    
    COLOR_SELECT = QColor(171, 0, 12, 30)
    COLOR_UNSELECT = QColor(171, 171, 171, 80)
    COLOR_BORDER = QColor(171, 0, 12)
    WIDTH_BORDER = 3
    
    def __init__(self, canvas, rectangle, bboxId):
        self.canvas = canvas
        self.rectangle = rectangle
        self.bboxId = bboxId
        super().__init__(self.canvas, QgsWkbTypes.PolygonGeometry)
        
        self.setToGeometry(QgsGeometry().fromRect(self.rectangle))
        self.setColor(self.COLOR_BORDER)
        self.setFillColor(self.COLOR_SELECT)
        self.setWidth(self.WIDTH_BORDER)
        self.selected = True
        self.xMin = self.rectangle.xMinimum()
        self.xMax = self.rectangle.xMaximum()
        self.yMin = self.rectangle.yMinimum()
        self.yMax = self.rectangle.yMaximum()
        self.show()
    
    def isInside(self, point):
        return self.xMin <= point.x() <= self.xMax and \
                self.yMin <= point.y() <= self.yMax

    def switchSelected(self):
        if self.selected:
            self.setFillColor(self.COLOR_UNSELECT)
        else:
            self.setFillColor(self.COLOR_SELECT)
        self.selected = not self.selected
        self.canvas.refresh()

