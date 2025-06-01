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
PATTERN_EXCLUDES = ['__pycache__', '.pro', '.ts', 'scripts/', 'test/']


def create_zip(zip_path, plugin_path, ignore_patterns):
    print('Creating ZIP archive ' + zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Readme is outside the plugin dir, so we start with it
        print('Adding README.md')
        zipf.write(os.path.join(plugin_path, os.pardir, 'README.md'),
                   'swissgeodownloader/README.md')
        # Go through all files in plugin dir and add them to zip archive
        for root, folders, files in os.walk(plugin_path):
            for file in files:
                path = str(os.path.join(root, file))
                archive_path = str(os.path.relpath(os.path.join(root, file),
                                                   os.path.join(plugin_path,
                                                                os.pardir)))
                if not any(fnmatch(path, '*' + ignore + '*') for ignore in ignore_patterns):
                    print('Adding ' + archive_path)
                    zipf.write(path, archive_path)
                else:
                    print('Ignoring ' + archive_path)
    print('Created ZIP archive ' + zip_path)


if __name__ == '__main__':
    # Path to plugin folder we want to deploy
    current_dir = os.path.dirname(__file__)
    # Create zip in plugin folder
    plugin_dir = os.path.join(current_dir, 'swissgeodownloader')
    zip_file = os.path.join(current_dir, PKG_NAME + '.zip')
    
    try:
        # Clean up
        os.remove(zip_file)
    except FileNotFoundError:
        pass
    
    # Zip content of plugin
    create_zip(zip_file, plugin_dir, PATTERN_EXCLUDES)
