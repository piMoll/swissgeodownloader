from qgis.PyQt.QtWidgets import QHeaderView, QTableView, QAbstractItemView
from qgis.PyQt.QtCore import QObject, QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel

class FileListTable(QObject):
    
    sig_selectionChanged = pyqtSignal(str, bool)
    
    def __init__(self, parent, layout):
        super().__init__()
        self.parent = parent
        self.tbl = QTableView(self.parent)
        self.tbl.setMinimumSize(QSize(0, 50))
        self.tbl.setAutoScroll(True)
        self.tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setObjectName("tbl")
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

    def fill(self, fileList):
        self.model.clear()
        
        # Insert data into cells
        for i, file in enumerate(fileList):
            item0 = QStandardItem()
            item1 = QStandardItem(file['id'])
            item1.setCheckState(Qt.Checked)
            item1.setCheckable(False)
            item1.setEditable(False)
            self.model.appendRow([item0, item1])

            self.model.setData(self.model.index(i, 0), Qt.Checked)
            self.model.setData(self.model.index(i, 1), file['id'])

        self.tbl.setFocusPolicy(Qt.NoFocus)
        self.tbl.hideColumn(0)

    def onClick(self, itemIdx):
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

    def clear(self):
        self.model.clear()

