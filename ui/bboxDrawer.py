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
    
    def __init__(self, canvas, transformer: QgsCoordinateTransform,
                 annotationManager: QgsAnnotationManager):
        self.canvas = canvas
        self.transformer = transformer
        self.annotationManager = annotationManager
        self.bboxItems = {}
    
    def paintBoxes(self, fileList):
        self.removeAll()
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
            html = ('<div style="font-size: 22px; text-align: center;">'
                    '<strong>' + str(idx+1) + '</strong></div>')
            a = QgsTextAnnotation()
            c = QTextDocument()
            c.setHtml(html)
            a.setDocument(c)
            a.setMarkerSymbol(None)
            a.setFillSymbol(None)
            labelPos = QgsPointXY(rectangle.center())
            a.setMapPosition(labelPos)
            a.setFrameSizeMm(QSizeF(24, 14))
            a.setFrameOffsetFromReferencePointMm(QPointF(-12, -5))
            a.setMapPositionCrs(self.transformer.destinationCrs())
            # Add annotation to annotation manager so it can be removed
            self.annotationManager.addAnnotation(a)
    
    def removeAll(self):
        for item in self.bboxItems.values():
            item.reset()
            del item
        self.bboxItems = {}
        for ann in self.annotationManager.annotations():
            self.annotationManager.removeAnnotation(ann)
    
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

