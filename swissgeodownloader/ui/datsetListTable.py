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
from qgis.PyQt.QtCore import (QCoreApplication, QObject, QSortFilterProxyModel,
                              Qt, pyqtSignal)
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import (QAbstractItemView, QAbstractScrollArea,
                                 QHeaderView, QLineEdit, QSizePolicy,
                                 QTableView)


class CollectionListTable(QObject):
    sig_selectionChanged = pyqtSignal(str)
    
    def __init__(self, parent, layout):
        super().__init__()
        self.parent = parent
        self.currentSelection = None
        
        self.tbl = QTableView(self.parent)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding,
                                 QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tbl.sizePolicy().hasHeightForWidth())

        self.model = QStandardItemModel(0, 0, self.tbl)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(2)
        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)
        self.tbl.setModel(self.proxy_model)

        self.tbl.setSizePolicy(sizePolicy)
        self.tbl.setMinimumHeight(90)
        self.tbl.setMaximumHeight(250)
        self.tbl.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tbl.setAutoScroll(True)
        
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setObjectName("DatasetListTable")
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tbl.verticalHeader().setDefaultSectionSize(20)

        self.searchbar = QLineEdit()
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.setPlaceholderText(self.tr('Search'))
        
        layout.addWidget(self.searchbar)
        layout.addWidget(self.tbl)

        self.searchbar.textChanged.connect(self.onSearch)
        self.tbl.clicked.connect(self.onClick)

    def fill(self, data):
        self.model.clear()
        
        # Insert data into cells
        for i, ds in enumerate(data):
            item0 = QStandardItem(ds.id)
            item0.setToolTip(ds.id)
            item0.setEditable(False)
            item1 = QStandardItem(ds.title)
            item1.setToolTip(ds.title)
            item1.setEditable(False)
            item2 = QStandardItem(ds.searchtext)
            item2.setEditable(False)
            self.model.appendRow([item0, item1, item2])
            self.model.setData(self.model.index(i, 0), ds.id)
            self.model.setData(self.model.index(i, 1), ds.title)
            self.model.setData(self.model.index(i, 2), ds.searchtext)
            
        self.model.setHorizontalHeaderLabels([self.tr('ID'), self.tr('Title'),
                                              self.tr('Search text')])
        self.tbl.setColumnWidth(0, 130)
        # Search text is not visible
        self.tbl.hideColumn(2)
    
    def onSearch(self, search):
        self.proxy_model.setFilterFixedString(search.lower())
        # Remove selection if the selected item is not visible anymore
        selectedIdx = self.tbl.selectionModel().selection().indexes()
        if selectedIdx and selectedIdx[0].data() != self.currentSelection:
            self.unselect()

    def onClick(self, itemIdx):
        dsId = itemIdx.siblingAtColumn(0).data()
        if dsId == self.currentSelection:
            self.unselect()
        else:
            self.currentSelection = dsId
            self.sig_selectionChanged.emit(dsId)
    
    def unselect(self):
        self.tbl.clearSelection()
        self.currentSelection = None
        self.sig_selectionChanged.emit(None)
    
    def resetSearch(self):
        self.searchbar.clear()

    def tr(self, message, **kwargs):
        return QCoreApplication.translate(type(self).__name__, message)

