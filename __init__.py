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
import os

__version__ = '2.0.1'

DEBUG = False
PLUGIN_DIR = os.path.dirname(__file__)
_AVAILABLE_LOCALES = ['de', 'en', 'it', 'fr']


def classFactory(iface):
    if DEBUG:
        try:
            # To allow remote debugging with PyCharm, add pydevd to the path
            import sys
            sys.path.append('/snap/pycharm-professional/current/debug-eggs/pydevd-pycharm.egg')
            import pydevd_pycharm
            pydevd_pycharm.settrace('localhost', port=53100, suspend=False,
                                    stdoutToServer=True, stderrToServer=True)
        except ConnectionRefusedError:
            pass
        except ImportError:
            pass
    
    from .swissgeodownloader import SwissGeoDownloader
    return SwissGeoDownloader(iface)
