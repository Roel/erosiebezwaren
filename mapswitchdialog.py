# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_mapswitchdialog import Ui_MapSwitchDialog

class MapSwitchDialog(QDialog, Ui_MapSwitchDialog):
    def __init__(self, action):
        self.action = action
        self.main = self.action.main
        QDialog.__init__(self)
        self.setupUi(self)

        self.visibleBase = set(['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart'])
        self.allLayers = set(['Orthofoto', 'Afstromingskaart', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie',
            'watererosie0', 'watererosie30', 'bewerkingserosie', 'dem_kul', 'dem_agiv', 'Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', 'Bodemkaart'])
        self.activeDem = None

        QObject.connect(self.btn_routekaart, SIGNAL('clicked(bool)'), self.toMapRoutekaart)
        QObject.connect(self.btn_orthofoto, SIGNAL('clicked(bool)'), self.toMapOrthofoto)
        QObject.connect(self.btn_erosie2013, SIGNAL('clicked(bool)'), self.toMapErosie2013)
        QObject.connect(self.btn_erosie2014, SIGNAL('clicked(bool)'), self.toMapErosie2014)
        QObject.connect(self.btn_erosie2015, SIGNAL('clicked(bool)'), self.toMapErosie2015)
        QObject.connect(self.btn_watererosie_0, SIGNAL('clicked(bool)'), self.toMapWatererosie0)
        QObject.connect(self.btn_watererosie_30, SIGNAL('clicked(bool)'), self.toMapWatererosie30)
        QObject.connect(self.btn_bewerkingserosie, SIGNAL('clicked(bool)'), self.toMapBewerkingserosie)
        QObject.connect(self.btn_afstromingskaart, SIGNAL('clicked(bool)'), self.toMapAfstromingskaart)
        QObject.connect(self.btn_dem_kul, SIGNAL('clicked(bool)'), self.toMapDEMKul)
        QObject.connect(self.btn_dem_agiv, SIGNAL('clicked(bool)'), self.toMapDEMAgiv)
        QObject.connect(self.btn_bodemkaart, SIGNAL('clicked(bool)'), self.toMapBodemkaart)

    def toggleLayersGroups(self, enable, disable):
        legendInterface = self.main.iface.legendInterface()

        groups = legendInterface.groups()
        for i in range(0, len(groups)):
            if groups[i] in enable:
                legendInterface.setGroupVisible(i, True)
            if groups[i] in disable:
                legendInterface.setGroupVisible(i, False)

        for l in legendInterface.layers():
            if l.name() in enable:
                legendInterface.setLayerVisible(l, True)
            if l.name() in disable:
                legendInterface.setLayerVisible(l, False)

    def toMapView(self, mapView):
        QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('extentsChanged()'), self.updateRasterColors)

        if mapView['autoDisable'] == True:
            mapView['disabledLayers'] = self.allLayers - mapView['enabledLayers']
        self.toggleLayersGroups(enable=mapView['enabledLayers'], disable=mapView['disabledLayers'])
        self.action.setText(mapView['label'])
        self.hide()

    def toMapRoutekaart(self):
        self.toMapView({
            'enabledLayers': self.visibleBase,
            'autoDisable': True,
            'label': 'Routekaart'
        })

    def toMapOrthofoto(self):
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['Topokaart'])).union(['Orthofoto']),
            'autoDisable': True,
            'label': 'Orthofoto'
        })

    def toMapErosie2013(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2013 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2013'
        })

    def toMapErosie2014(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2014 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2014'
        })

    def toMapErosie2015(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2015 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2015'
        })

    def toMapWatererosie30(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['watererosie30']),
            'autoDisable': True,
            'label': 'Watererosie 30'
        })

    def toMapWatererosie0(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['watererosie0']),
            'autoDisable': True,
            'label': 'Watererosie 0'
        })

    def toMapBewerkingserosie(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['bewerkingserosie']),
            'autoDisable': True,
            'label': 'Bewerkingserosie'
        })

    def toMapAfstromingskaart(self):
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['bezwarenkaart', 'percelenkaart', 'Overzichtskaart'])).union(['Afstromingskaart']),
            'autoDisable': True,
            'label': 'Afstromingskaart'
        })

    def toMapDEMKul(self):
        self.activeDem = self.main.utils.getLayerByName('dem_kul')
        self.updateRasterColors()

        self.toMapView({
            'enabledLayers': self.visibleBase.union(['dem_kul']),
            'autoDisable': True,
            'label': 'DEM KULeuven'
        })

        QObject.connect(self.main.iface.mapCanvas(), SIGNAL('extentsChanged()'), self.updateRasterColors)

    def toMapDEMAgiv(self):
        self.activeDem = self.main.utils.getLayerByName('dem_agiv')
        self.updateRasterColors()

        self.toMapView({
            'enabledLayers': self.visibleBase.union(['dem_agiv']),
            'autoDisable': True,
            'label': 'DEM AGIV'
        })

        QObject.connect(self.main.iface.mapCanvas(), SIGNAL('extentsChanged()'), self.updateRasterColors)

    def toMapBodemkaart(self):
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['Topokaart'])).union(['Bodemkaart']),
            'autoDisable': True,
            'label': 'Bodemkaart'
        })

    def updateRasterColors(self):
        if not self.activeDem:
            return

        currentExtent = self.main.iface.mapCanvas().extent()
        bandStats = self.activeDem.dataProvider().bandStatistics(1, QgsRasterBandStats.Max | QgsRasterBandStats.Min, currentExtent, 1000)
        vmax = bandStats.maximumValue
        vmin = bandStats.minimumValue

        colorList = [QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*0+vmin, QColor('#2b83ba')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*1+vmin, QColor('#abdda4')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*2+vmin, QColor('#ffffbf')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*3+vmin, QColor('#fdae61')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*4+vmin, QColor('#d7191c'))]

        rasterShader = QgsRasterShader()
        colorRampShader = QgsColorRampShader()
        colorRampShader.setColorRampItemList(colorList)
        colorRampShader.setColorRampType(QgsColorRampShader.INTERPOLATED)
        rasterShader.setRasterShaderFunction(colorRampShader)
        pseudoColorRenderer = QgsSingleBandPseudoColorRenderer(self.activeDem.dataProvider(), self.activeDem.type(), rasterShader)
        self.activeDem.setRenderer(pseudoColorRenderer)
        self.activeDem.triggerRepaint()

class MapSwitchButton(QToolButton):
    def __init__(self, main, parent):
        self.main = main
        QToolButton.__init__(self, parent)
        self.dialog = MapSwitchDialog(self)

        self.setText('Kies kaartbeeld')
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        self.setMinimumHeight(64)

        QObject.connect(self, SIGNAL('clicked(bool)'), self.showDialog)

    def showDialog(self):
        self.dialog.move(0, 0)
        self.dialog.show()
