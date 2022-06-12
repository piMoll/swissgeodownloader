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
from qgis.PyQt.QtWidgets import (QHeaderView, QTableView, QAbstractItemView,
                                 QSizePolicy, QAbstractScrollArea)
from qgis.PyQt.QtCore import QObject, Qt, pyqtSignal
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel, QFont

class FileListTable(QObject):
    
    sig_selectionChanged = pyqtSignal(str, bool)
    
    def __init__(self, parent, layout):
        super().__init__()
        self.parent = parent
        self.tbl = QTableView(self.parent)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbl.sizePolicy().hasHeightForWidth())
        self.tbl.setSizePolicy(sizePolicy)
        self.tbl.setMinimumHeight(160)
        self.tbl.setMaximumHeight(1200)
        self.tbl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tbl.setAutoScroll(True)
        
        self.tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setObjectName("FileListTable")
        self.tbl.horizontalHeader().setVisible(False)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.verticalHeader().setVisible(True)
        self.tbl.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tbl.verticalHeader().setDefaultSectionSize(24)
        layout.addWidget(self.tbl)

        self.model = QStandardItemModel(0, 0, self.tbl)
        self.tbl.setModel(self.model)
        
        self.tbl.hideColumn(0)
        self.tbl.clicked.connect(self.onClick)
        
        self.showEmptyMessage = False

    def fill(self, fileList):
        self.model.clear()
        self.showEmptyMessage = False
        
        # Insert data into cells
        for i, file in enumerate(fileList):
            item0 = QStandardItem()
            item1 = QStandardItem(file.id)
            item1.setCheckState(Qt.Checked)
            item1.setCheckable(False)
            item1.setEditable(False)
            
            self.model.appendRow([item0, item1])
            self.model.setData(self.model.index(i, 0), Qt.Checked)
            self.model.setData(self.model.index(i, 1), file.id)

        self.tbl.setFocusPolicy(Qt.NoFocus)
        self.tbl.hideColumn(0)

    def onClick(self, itemIdx):
        if self.showEmptyMessage:
            return
        
        fileId = itemIdx.data()
        FileIdItem = self.model.item(itemIdx.row(), itemIdx.column())
        
        checkStateIdx = self.model.index(itemIdx.row(), 0)
        checkStateData = self.model.data(checkStateIdx)

        if checkStateData == Qt.Checked:
            self.model.setData(checkStateIdx, Qt.Unchecked)
            FileIdItem.setCheckState(Qt.Unchecked)
            self.sig_selectionChanged.emit(fileId, False)
        else:
            self.model.setData(checkStateIdx, Qt.Checked)
            FileIdItem.setCheckState(Qt.Checked)
            self.sig_selectionChanged.emit(fileId, True)
    
    def onEmptyList(self, message):
        self.model.clear()
        item0 = QStandardItem()
        item1 = QStandardItem(message)
        item1.setEditable(False)
        italicFont = QFont()
        italicFont.setItalic(True)
        item1.setFont(italicFont)
        
        self.model.appendRow([item0, item1])
        self.showEmptyMessage = True
        self.tbl.setFocusPolicy(Qt.NoFocus)
        self.tbl.hideColumn(0)

    def clear(self):
        self.model.clear()
        self.showEmptyMessage = False
