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
from qgis.PyQt.QtWidgets import (QTableView, QAbstractItemView, QLineEdit,
                                 QSizePolicy, QAbstractScrollArea, QHeaderView)
from qgis.PyQt.QtCore import (QObject, Qt, pyqtSignal, QSortFilterProxyModel,
                              QCoreApplication)
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel


class DatasetListTable(QObject):
    sig_selectionChanged = pyqtSignal(str)
    
    def __init__(self, parent, layout):
        super().__init__()
        self.parent = parent
        self.currentSelection = None
        
        self.tbl = QTableView(self.parent)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tbl.sizePolicy().hasHeightForWidth())
        self.tbl.setSizePolicy(sizePolicy)
        self.tbl.setMinimumHeight(160)
        self.tbl.setMaximumHeight(200)
        self.tbl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tbl.setAutoScroll(True)
        
        self.tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setObjectName("DatasetListTable")
        self.tbl.horizontalHeader().setVisible(False)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tbl.verticalHeader().setDefaultSectionSize(20)

        self.model = QStandardItemModel(0, 0, self.tbl)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.sort(0, Qt.AscendingOrder)
        self.tbl.setModel(self.proxy_model)
        self.tbl.hideColumn(1)

        self.searchbar = QLineEdit()
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.setPlaceholderText(self.tr('Search'))
        self.searchbar.textChanged.connect(self.onSearch)
        
        layout.addWidget(self.searchbar)
        layout.addWidget(self.tbl)
        
        self.tbl.clicked.connect(self.onClick)

    def fill(self, data):
        self.model.clear()
        
        # Insert data into cells
        for i, ds in enumerate(data):
            item0 = QStandardItem(ds.id)
            item0.setEditable(False)
            item1 = QStandardItem(ds.description)
            item1.setEditable(False)
            self.model.appendRow([item0, item1])
            self.model.setData(self.model.index(i, 0), ds.id)
            self.model.setData(self.model.index(i, 1), ds.description)

        self.tbl.hideColumn(1)
    
    def onSearch(self, search):
        self.searchbar.blockSignals(True)
        if self.currentSelection:
            self.unselect()
        self.proxy_model.setFilterFixedString(search)
        self.tbl.setFocusPolicy(Qt.NoFocus)
        self.searchbar.blockSignals(False)
    
    def onClick(self, itemIdx):
        dsId = itemIdx.data(0)
        if dsId == self.currentSelection:
            self.unselect()
        else:
            self.currentSelection = dsId
            self.sig_selectionChanged.emit(dsId)
    
    def unselect(self):
        self.tbl.clearSelection()
        self.currentSelection = None
        self.sig_selectionChanged.emit(None)

    def tr(self, message, **kwargs):
        return QCoreApplication.translate(type(self).__name__, message)

