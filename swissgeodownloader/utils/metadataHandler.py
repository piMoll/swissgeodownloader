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
import json
import os
from datetime import date

from qgis.core import Qgis, QgsMessageLog, QgsSettings

from swissgeodownloader.utils.ui_utilities import MESSAGE_CATEGORY

SETTING_PREFIX = 'PluginSwissGeoDownloader'
PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))
SAVE_DIRECTORY = os.path.join(PLUGIN_PATH, 'api')


def saveToFile(metadata, filename):
    try:
        jsonData = json.dumps(metadata, indent=2, sort_keys=True,
                              ensure_ascii=False)
    except Exception:
        log('Converting metadata to json data not successful')
        return
    
    metafile = os.path.join(SAVE_DIRECTORY, filename)
    try:
        with open(metafile, 'w', encoding='utf8') as f:
            f.write(jsonData)
    except PermissionError:
        log('Saving metadata to json file not successful')


def loadFromFile(filename):
    filepath = os.path.join(SAVE_DIRECTORY, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            log('Loading metadata from file not possible')
            return {}
    else:
        log('Metadata file not found')


def saveToSettings(collectionId, metadata, locale):
    s = QgsSettings()
    settingsPath = f"{SETTING_PREFIX}/metadata/{collectionId}/{locale}"
    
    today = date.today()
    s.setValue(f"{settingsPath}/title", metadata['title'])
    s.setValue(f"{settingsPath}/abstract", metadata['abstract'])
    s.setValue(f"{settingsPath}/date", today.isoformat())


def loadFromSettings(collectionId, locale):
    # Read out metadata from QGIS settings
    s = QgsSettings()
    settingsPath = f"{SETTING_PREFIX}/metadata/{collectionId}/{locale}"
    
    updateDateStr = s.value(f"{settingsPath}/date", None)
    if not updateDateStr:
        log('Loading from settings not successful, no date')
        return None
    
    try:
        updateDate = date.fromisoformat(updateDateStr)
    except Exception:
        log('Loading from settings not successful, update date not valid')
        return None
    
    # Check if metadata ist still up to date
    today = date.today()
    if (today - updateDate).days > 60:
        s.remove(f"{settingsPath}")
        return None
    
    return {
        'title': s.value(f"{settingsPath}/title", ''),
        'abstract': s.value(f"{settingsPath}/abstract", ''),
        }


def log(msg, level=Qgis.MessageLevel.Info):
    QgsMessageLog.logMessage(str(msg), MESSAGE_CATEGORY, level)
