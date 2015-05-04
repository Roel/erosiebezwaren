# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class AttributeModel(QAbstractItemModel):
    def __init__(self, parent, layer, attributeName):
        self.layer = layer
        self.attributeName = attributeName
        QAbstractItemModel.__init__(self, parent)

        self.values = []
        self.updateValues()

    def updateValues(self):
        values = [''] #FIXME
        for feature in self.layer.getFeatures():
            v = feature.attribute(self.attributeName)
            if v not in values:
                values.append(v)
        self.values = values

    def columnCount(self, parent):
        return 1

    def rowCount(self, parent):
        return len(self.values)

    def index(self, row, col, parent):
        return self.createIndex(row, col, None)

    def parent(self, index):
        return QModelIndex()

    def data(self, index, role):
        return self.values[index.row()]

class AttributeFilledCombobox(QComboBox):
    def __init__(self, parent, layer=None, attributename=None):
        QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.parent = parent
        self.layer = layer
        self.attributename = attributename

        if layer and attributename:
            self.model = AttributeModel(self.parent, self.layer, self.attributename)
            self.setModel(self.model)

    def setSource(self, layer, attributename):
        self.layer = layer
        self.attributename = attributename

        if layer and attributename:
            self.model = AttributeModel(self.parent, self.layer, self.attributename)
            self.setModel(self.model)

    def setValue(self, value):
        if value:
            self.lineEdit().setText(value)
        else:
            self.lineEdit().clear()

    def getValue(self):
        return self.lineEdit().text()
