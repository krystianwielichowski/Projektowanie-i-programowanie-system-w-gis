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
from PyQt4.QtGui import QAction, QIcon, QColor
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from pogodynka_dialog import PogodynkaDialog

#from ustawienia_dialog import UstawieniaDialog
import os.path
import urllib2
import json
import datetime
from qgis.core import *
import os
import qgis
from qgis.utils import iface
import processing
import PyQt4.QtGui


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
        #self.ustDlg = UstawieniaDialog()
        

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
            callback=self.aktualizujDane)
        self.add_action(
            icon_path,
            text=self.tr(u'Ustawienia'),
            callback=self.ustawienia)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pogodynka'),
                action)
            self.iface.removeToolBarIcon(action)


    def aktualizujDane(self):
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
                    iface.messageBar().pushMessage(u"Dane zaktualizowano.", 0, 20)
                    
                else:
                    iface.messageBar().pushMessage(u"Brak potrzeby aktualizacji danych.", 0, 20)
            except IOError:
                plik = open(pliktxt, 'w')
                plik.write(str(bierzacyCzas))
                plik.close()
                aktualizujDane()
                iface.messageBar().pushMessage(u"Dane zaktualizowano.", 0, 20)
            
            
            QgsMapLayerRegistry.instance().removeAllMapLayers ()
            QgsMapLayerRegistry.instance().addMapLayer(woj)
                    
            pass

    def ustawienia(self):
        ustawienia = self.plugin_dir + '/ustawienia.txt'
        plik = open(ustawienia, 'r')
        ust = plik.readline()
        plik.close()
        combo = int(ust[:1])
        check1 = int(ust[2:3])
        check2 = int(ust[4:5])
        self.dlg.comboBox.setCurrentIndex(combo);
        if check1 == 1:
            self.dlg.checkBox.setCheckState(2)
        else:
            self.dlg.checkBox.setCheckState(0)

        if check2 == 1:
            self.dlg.checkBox_2.setCheckState(2)
        else:
            self.dlg.checkBox_2.setCheckState(0)


        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            plik = open(ustawienia, 'w')
            plik.write(str(self.dlg.comboBox.currentIndex()) + ' ')
            plik.write(str(int(self.dlg.checkBox.isChecked())) + ' ')
            plik.write(str(int(self.dlg.checkBox_2.isChecked())))
            plik.close()
            warstwa = QgsMapLayerRegistry.instance().mapLayersByName('wojewodztwa')
            shp = self.plugin_dir + '/dane/wojewodztwa/wojewodztwa.shp'
            myVectorLayer = QgsVectorLayer(shp, 'wojewodztwa', 'ogr')

            
            myVectorLayer.setCustomProperty("labeling", "pal")
            myVectorLayer.setCustomProperty("labeling/fontFamily", "Arial")
            myVectorLayer.setCustomProperty("labeling/fontSize", "10")
            myVectorLayer.setCustomProperty("labeling/fontColor", '#ffffff') 
            myVectorLayer.setCustomProperty("labeling/placement", "0")
            myVectorLayer.setCustomProperty("labeling/fieldName", "Temp")
            myVectorLayer.setCustomProperty("labeling/bufferColorA", "255")
            myVectorLayer.setCustomProperty("labeling/bufferColorB", "255")
            myVectorLayer.setCustomProperty("labeling/bufferColorG", "255")
            myVectorLayer.setCustomProperty("labeling/bufferColorR", "255")
            myVectorLayer.setCustomProperty("labeling/bufferJoinStyle", "64")
            myVectorLayer.setCustomProperty("labeling/bufferNoFill", "false")
            myVectorLayer.setCustomProperty("labeling/bufferSize", "1")
            myVectorLayer.setCustomProperty("labeling/bufferDraw", "true")
            
        if combo != 0:
            if combo == 1:
                myTargetField = 'temp'
                myRangeList = []
                myOpacity = 1
                # Make our first symbol and range...
                myMin = 30.1
                myMax = 50.0
                myLabel = '30 - 50 C'
                myColour = QColor('#ff0000')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)
                #now make another symbol and range...
                myMin = 20.1
                myMax = 30.0
                myLabel = '20 - 30'
                myColour = QColor('#ff8800')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)
                
                myMin = 10.1
                myMax = 20.0
                myLabel = '10 - 20'
                myColour = QColor('#ffff00')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)
                
                myMin = 0.1
                myMax = 10.0
                myLabel = '0 - 10'
                myColour = QColor('#88ff00')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = -10
                myMax = 0
                myLabel = '-10 - 0'
                myColour = QColor('#00ffff')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)
                
                myMin = -20
                myMax = -10.1
                myLabel = '-20 - -10'
                myColour = QColor('#0099ff')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = -30
                myMax = -20.1
                myLabel = '-30 - -20'
                myColour = QColor('#0044ff')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)
                
                myMin = -50
                myMax = -30.1
                myLabel = '-50 - -30'
                myColour = QColor('#0000ff')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
                myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
                myRenderer.setClassAttribute(myTargetField)
                myVectorLayer.setRendererV2(myRenderer)
            if combo == 2:
                myTargetField = 'wilgotnosc'
                myRangeList = []
                myOpacity = 1
                # Make our first symbol and range...
                myMin = 75.1
                myMax = 100.0
                myLabel = '75 - 100 %'
                myColour = QColor('#090149')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 50.1
                myMax = 75.0
                myLabel = '50 - 75'
                myColour = QColor('#2376ea')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 25.1
                myMax = 50.0
                myLabel = '25 - 50'
                myColour = QColor('#77a9ef')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 0
                myMax = 25.0
                myLabel = '0 - 25'
                myColour = QColor('#e0eeff')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
                myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
                myRenderer.setClassAttribute(myTargetField)
                myVectorLayer.setRendererV2(myRenderer)
            if combo == 3:
                myTargetField = 'vWiatr'
                myRangeList = []
                myOpacity = 1
                # Make our first symbol and range...
                myMin = 20.1
                myMax = 50
                myLabel = '20 - 50 m/s'
                myColour = QColor('#ff0000')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 10.1
                myMax = 20
                myLabel = '10 - 20'
                myColour = QColor('#ff5555')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 5.1
                myMax = 10
                myLabel = '5 - 10'
                myColour = QColor('#ffaaaa')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 0
                myMax = 5
                myLabel = '0 - 5'
                myColour = QColor('#ffeeee')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
                myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
                myRenderer.setClassAttribute(myTargetField)
                myVectorLayer.setRendererV2(myRenderer)
            if combo == 4:
                myTargetField = 'chmury'
                myRangeList = []
                myOpacity = 1
                # Make our first symbol and range...
                myMin = 75.1
                myMax = 100.0
                myLabel = '75 - 100 %'
                myColour = QColor('#111111')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 50.1
                myMax = 75.0
                myLabel = '50 - 75'
                myColour = QColor('#555555')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 25.1
                myMax = 50.0
                myLabel = '25 - 50'
                myColour = QColor('#aaaaaa')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myMin = 0
                myMax = 25.0
                myLabel = '0 - 25'
                myColour = QColor('#eeeeee')
                mySymbol1 = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
                mySymbol1.setColor(myColour)
                mySymbol1.setAlpha(myOpacity)
                myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                myRangeList.append(myRange1)

                myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
                myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
                myRenderer.setClassAttribute(myTargetField)
                myVectorLayer.setRendererV2(myRenderer)
        else:
            myColour = QColor('#ffffff')
            mySymbol = QgsSymbolV2.defaultSymbol(myVectorLayer.geometryType())
            mySymbol.setColor(myColour)
            mySymbol.setAlpha(1)

            myRenderer = QgsSingleSymbolRendererV2(mySymbol)
            #myRenderer.setSymbol(mySymbol)
            myVectorLayer.setRendererV2(myRenderer)
            
        if check1 == 1:
            myVectorLayer.setCustomProperty("labeling/enabled", "true")
        else:
            myVectorLayer.setCustomProperty("labeling/enabled", "false")
                

        diagram = QgsPieDiagram() 
        ds = QgsDiagramSettings() 
        ds.transparency = 0
        
        ds.categoryAttributes = ['chmury'] 
        dColors = {1:QColor("blue")} 
        ds.categoryColors = dColors.values() 
        ds.categoryIndices = dColors.keys() 
        ds.labelPlacementMethod = 1 
        ds.scaleByArea = True 
        ds.minimumSize = 0 
        ds.BackgroundColor = QColor(255,255,255,0)
        ds.PenColor = QColor("black")
        ds.penWidth = 0
        ds.minScaleDenominator = -1; 
        ds.maxScaleDenominator = -1; 
        dr = QgsLinearlyInterpolatedDiagramRenderer()
        dr.setLowerValue(0)
        dr.setLowerSize( PyQt4.QtCore.QSizeF( 0.0, 0.0 ) )
        dr.setUpperValue(100)
        dr.setUpperSize( PyQt4.QtCore.QSizeF(15,15) )
        dr.setClassificationAttribute(9)
        dr.setDiagram( diagram )
        dr.setDiagramSettings( ds )
        
        dls = QgsDiagramLayerSettings() 
        dls.dist = 0
        dls.priority = 0
        dls.xPosColumn = -1  
        dls.yPosColumn = -1
        dls.placement = 0 
        
        if check2 == 1:
            myVectorLayer.setDiagramRenderer( dr ) 
            myVectorLayer.setDiagramLayerSettings( dls )

        QgsMapLayerRegistry.instance().removeAllMapLayers ()
        QgsMapLayerRegistry.instance().addMapLayer(myVectorLayer)
        qgis.utils.iface.mapCanvas().refresh()
        pass
    pass

        
