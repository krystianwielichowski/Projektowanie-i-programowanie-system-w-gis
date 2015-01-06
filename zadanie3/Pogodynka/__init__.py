# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogodynka
                                 A QGIS plugin
 Aktualizuj dane atmosferyczne
                             -------------------
        begin                : 2015-01-05
        copyright            : (C) 2015 by Krystian Wielichowski
        email                : q@eh.pl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Pogodynka class from file Pogodynka.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pogodynka import Pogodynka
    return Pogodynka(iface)
