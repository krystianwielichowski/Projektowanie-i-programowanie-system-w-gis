# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogodynka
                                 A QGIS plugin
 Aktualizuj dane atmosferyczne
                              -------------------
        begin                : 2015-01-05
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Krystian Wielichowski
        email                : q@eh.pl
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from pogodynka_dialog import PogodynkaDialog
import os.path
import urllib2
import json
import datetime
from qgis.core import *
import os


class Pogodynka:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Pogodynka_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PogodynkaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pogodynka')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Pogodynka')
        self.toolbar.setObjectName(u'Pogodynka')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Pogodynka', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Pogodynka/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Aktualizuj dane'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pogodynka'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            shp = self.plugin_dir + '/dane/wojewodztwa/wojewodztwa.shp'
            woj = QgsVectorLayer(shp, 'wojewodztwa', 'ogr')
            pliktxt = self.plugin_dir + '/dane/dataAktualizacji.txt'
            def aktualizujDane():
                listaID=''
                for w in woj.getFeatures():
                    if listaID=='':
                        listaID = str(w.attributes()[1])
                    else:
                        listaID = listaID + ',' + str(w.attributes()[1])
                
                url = 'http://api.openweathermap.org/data/2.5/group?id=' + listaID + '&units=metric'
                content = urllib2.urlopen(url).read()
                slownik = json.loads(content)
                for w in woj.getFeatures():
                    for i in xrange(0, len(slownik['list'])):
                        if w.attributes()[1] == slownik['list'][i]['id']:
                            aTemp ={woj.fieldNameIndex('temp'):slownik['list'][i]['main']['temp']}
                            aTempMAX ={woj.fieldNameIndex('tempMAX'): slownik['list'][i]['main']['temp_max']}
                            aTempMIN ={woj.fieldNameIndex('tempMIN'): slownik['list'][i]['main']['temp_min']}
                            aTempMIN ={woj.fieldNameIndex('tempMIN'): slownik['list'][i]['main']['temp_min']}
                            aCis={woj.fieldNameIndex('cisnienie'): slownik['list'][i]['main']['pressure']}
                            aWil={woj.fieldNameIndex('wilgotnosc'): slownik['list'][i]['main']['humidity']}
                            aVW={woj.fieldNameIndex('vWiatr'): slownik['list'][i]['wind']['speed']}
                            aKierW={woj.fieldNameIndex('kierWiatr'): slownik['list'][i]['wind']['deg']}
                            aChmury={woj.fieldNameIndex('chmury'): slownik['list'][i]['clouds']['all']}
                            woj.startEditing()
                            woj.dataProvider().changeAttributeValues({w.id():aTemp})
                            woj.dataProvider().changeAttributeValues({w.id():aTempMAX})
                            woj.dataProvider().changeAttributeValues({w.id():aTempMIN})
                            woj.dataProvider().changeAttributeValues({w.id():aCis})
                            woj.dataProvider().changeAttributeValues({w.id():aWil})
                            woj.dataProvider().changeAttributeValues({w.id():aVW})
                            woj.dataProvider().changeAttributeValues({w.id():aKierW})
                            woj.dataProvider().changeAttributeValues({w.id():aChmury})
                            woj.commitChanges()
            
            
            minimalnyOdstep = datetime.timedelta(0, 0, 0, 0, 10)
            bierzacyCzas = datetime.datetime.now()
            
            try:
                plik = open(pliktxt, 'r')
                poprzedni = plik.readline()
                plik.close()
                poprzedniaAktualizacja = datetime.datetime(int(poprzedni[:4]), int(poprzedni[5:7]), int(poprzedni[8:10]), int(poprzedni[11:13]), int(poprzedni[14:16]), int(poprzedni[17:19]), int(poprzedni[20:]))
                if bierzacyCzas - poprzedniaAktualizacja > minimalnyOdstep:
                    aktualizujDane()
                    plik = open(pliktxt, 'w')
                    plik.write(str(bierzacyCzas))
                    plik.close()
                    print 'Dane zaktualizowano'
                else:
                    print 'Brak potrzeby aktualizacji danych'
            except IOError:
                plik = open(pliktxt, 'w')
                plik.write(str(bierzacyCzas))
                plik.close()
                aktualizujDane()
                print 'Dane zaktualizowano'
            QgsMapLayerRegistry.instance().addMapLayer(woj)
            pass
