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
import os
import zipfile
from fnmatch import fnmatch

PKG_NAME = 'swissgeodownloader'
TOP_LEVEL_INCLUDES = [
    'api',
    'i18n',
    'resources',
    'ui',
    'utils',
    '__init__.py',
    'CHANGELOG.md',
    'LICENSE',
    'metadata.txt',
    'README.md',
    'swissgeodownloader.py',
]
PATTERN_EXCLUDES = [
    '__pycache__',
    '.pro',
    '.ts',
]


def create_zip(zip_path, folder_path, top_level_includes, ignore_patterns):
    print('Creating ZIP archive ' + zip_path)
    includedPaths = [os.path.join(folder_path, folder) for folder in
                     top_level_includes]
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, folders, files in os.walk(folder_path):
            for file in files:
                path = str(os.path.join(root, file))
                if any([path.startswith(str(includedPath)) for includedPath in
                        includedPaths]) is False:
                    # Path does not start with a path from the include list, skip it
                    continue
                archive_path = str(os.path.relpath(
                    os.path.join(root, file),
                    os.path.join(folder_path, os.pardir)))
                if not any(fnmatch(path, '*' + ignore + '*') for ignore in ignore_patterns):
                    print('Adding ' + archive_path)
                    zipf.write(path, archive_path)
                else:
                    print('Ignoring ' + archive_path)
    print('Created ZIP archive ' + zip_path)


if __name__ == '__main__':
    # Path to plugin folder we want to deploy
    plugin_dir = os.path.dirname(__file__)
    # Create zip in plugin folder
    deploy_path = plugin_dir
    zip_file = os.path.join(deploy_path, PKG_NAME + '.zip')
    
    try:
        # Clean up
        os.remove(zip_file)
    except FileNotFoundError:
        pass
    
    # Zip content of plugin
    create_zip(zip_file, plugin_dir, TOP_LEVEL_INCLUDES, PATTERN_EXCLUDES)
