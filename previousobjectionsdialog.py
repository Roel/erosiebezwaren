# -*- coding: utf-8 -*-
"""Module for the dialog for listing previous objections for a parcel.

Contains the PreviousObjectionsWidget and previousObjectionsDialog classes.
"""

#  DOV Erosiebezwaren, QGis plugin to assess field erosion on tablets
#  Copyright (C) 2015-2017  Roel Huybrechts
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import qgis.core as QGisCore

from ui_previousobjectionsdialog import Ui_PreviousObjectionsDialog

from previousobjectioninfodialog import PreviousObjectionInfoDialog
from qgsutils import SpatialiteIterator
from widgets import valuelabel


class PreviousObjectionsWidget(QtGui.QWidget):
    """Widget showing a list of previous objections for a given parcel."""

    def __init__(self, uniek_id, parent, previousObjectionsDialog):
        """Initialisation.

        Parameters
        ----------
        uniek_id : str
            Unique identification number, 'uniek_id' attribute, of the parcel.
        parent : QtGui.QWidget
            Widget to use as parent widget.
        previousObjectionsDialog : PreviousObjectionsDialog
            Instance of PreviousObjectionsDialog this widget belongs to.

        """
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.uniek_id = uniek_id
        self.previousObjectionsDialog = previousObjectionsDialog
        self.main = self.previousObjectionsDialog.main
        self.previousObjectionsLayer = self.main.utils.getLayerByName(
            self.main.settings.getValue('layers/oudebezwaren'))

        self.horMaxSizePolicy = QtGui.QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QtGui.QSizePolicy.Maximum)

        self.layout = QtGui.QGridLayout(parent)
        self.setLayout(self.layout)

        lb_jaar = QtGui.QLabel('<b>Jaar</b>')
        lb_jaar.setSizePolicy(self.horMaxSizePolicy)
        self.layout.addWidget(lb_jaar, 0, 0)
        self.layout.addWidget(QtGui.QLabel('<b>Oorsprokelijk</b>'), 0, 1)
        self.layout.addWidget(QtGui.QLabel('<b>Advies</b>'), 0, 2)
        self.layout.addWidget(QtGui.QLabel('<b>Aanpassing</b>'), 0, 3)
        self.layout.addWidget(QtGui.QLabel('<b>Details</b>'), 0, 4)
        self.__populate()

    def __populate(self):
        """Find all previous objections for the parcel and add them."""
        if not self.previousObjectionsLayer:
            return

        expr = '"perceel_2018" like \'%%%s%%\'' % (self.uniek_id)
        objectionList = []
        for i in self.previousObjectionsLayer.getFeatures(
                QGisCore.QgsFeatureRequest(QGisCore.QgsExpression(expr))):
            objectionList.append(i)

        filteredObjectionList = []
        for i in objectionList:
            perceel_2018 = i.attribute('perceel_2018').split(',')
            if self.uniek_id in perceel_2018:
                filteredObjectionList.append(i)

        for i in sorted(filteredObjectionList,
                        key=lambda x: int(x.attribute('jaar'))):
            self.addObjection(i)

    def addObjection(self, feature):
        """Add a previous objection to the list.

        Parameters
        ----------
        feature : QGisCore.QgsFeature
            Feature representing the previous objection.

        """
        row = self.layout.rowCount()

        btnJaar = QtGui.QPushButton(str(feature.attribute('jaar')), self)
        btnJaar.setSizePolicy(self.horMaxSizePolicy)
        QtCore.QObject.connect(btnJaar, QtCore.SIGNAL('clicked(bool)'),
                               lambda: self.highlightObjection(feature))
        self.layout.addWidget(btnJaar, row, 0)

        lb1 = valuelabel.ValueLabel(self)
        lb1.setText(feature.attribute('voor'))
        self.layout.addWidget(lb1, row, 1)

        lb2 = valuelabel.ValueLabel(self)
        lb2.setText(feature.attribute('advies'))
        self.layout.addWidget(lb2, row, 2)

        lb3 = valuelabel.ValueLabel(self)
        lb3.setText(feature.attribute('na'))
        self.layout.addWidget(lb3, row, 3)

        if feature.attribute('jaar') >= 2015:
            btnDetails = QtGui.QPushButton('info', self)
            QtCore.QObject.connect(btnDetails, QtCore.SIGNAL('clicked(bool)'),
                                   lambda: self.showInfo(feature))
            btnDetails.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(btnDetails, row, 4)

    def highlightObjection(self, feature):
        """Select the given objection in a distinctive color.

        Parameters
        ----------
        feature : QGisCore.QgsFeature
            Feature of the objection to select.

        """
        self.main.selectionManagerPolygons.clearWithMode(mode=2,
                                                         toggleRendering=False)
        self.main.selectionManagerPolygons.select(feature, mode=2)

    def showInfo(self, feature):
        """Show more info of the given objection using a second dialog.

        Creates a PreviousObjectionInfoDialog with more info about the
        given objection.

        Parameters
        ----------
        feature : QGisCore.QgsFeature
            Feature of the objection to show information about.

        """
        def clearHighlightedObjections():
            self.main.selectionManagerPolygons.clearWithMode(mode=2)

        self.highlightObjection(feature)

        s = SpatialiteIterator(self.main.utils.getLayerByName(
            'bezwaren_%i' % feature.attribute('jaar')))
        oldFt = s.queryExpression("uniek_id = '%s'" %
                                  feature.attribute('oud_bezwaar_id'))[0]

        d = PreviousObjectionInfoDialog(self.parent, self.main, oldFt,
                                        feature.attribute('jaar'))
        QtCore.QObject.connect(d, QtCore.SIGNAL('finished(int)'),
                               clearHighlightedObjections)
        d.show()


class PreviousObjectionsDialog(QtGui.QDialog, Ui_PreviousObjectionsDialog):
    """Dialog showing a list previous objections for a given parcel."""

    def __init__(self, main, uniek_id):
        """Initialisation.

        Create a PreviousObjectionsWidget containing the list of previous
        objections.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        uniek_id : str
            Unique identification number, 'uniek_id' attribute, of the parcel.

        """
        self.main = main
        self.uniek_id = uniek_id
        QtGui.QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        QtCore.QObject.connect(self, QtCore.SIGNAL('finished(int)'), self.exit)

        self.lbv_uniek_id.setText('Oude bezwaren voor perceel %s' %
                                  self.uniek_id)
        self.scrollAreaLayout.insertWidget(0, PreviousObjectionsWidget(
            self.uniek_id, self.scrollAreaWidgetContents, self))

    def exit(self):
        """Clear the selection of previous objections.

        Called upon closing the dialog.
        """
        self.main.selectionManagerPolygons.clearWithMode(mode=2)
