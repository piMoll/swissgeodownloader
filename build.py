import os
import sys
import subprocess
from fnmatch import fnmatch
import zipfile
from shutil import rmtree

PKG_NAME = 'swissgeodownloader'
ZIP_EXCLUDES = [
    '__pycache__',
    '.pro',
    '.ts',
    'help/',
    'abstractApiConnector.py',
    'network2.py',
    'networkaccess.py',
    'networkmanager.py',
]


def create_zip(zip_path, folder_path, ignore_patterns):
    print('Creating ZIP archive ' + zip_path)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                path = os.path.join(root, file)
                archive_path = os.path.relpath(os.path.join(root, file), os.path.join(folder_path, os.pardir))
                if not any(fnmatch(path, '*' + ignore + '*') for ignore in ignore_patterns):
                    print('Adding ' + archive_path)
                    zipf.write(path, archive_path)
                else:
                    print('Ignoring ' + archive_path)
    print('Created ZIP archive ' + zip_path)


if __name__ == '__main__':
    # Deploy to another qgis profile for testing and packing
    qgis_profile = sys.argv[0]
    run_pb_tool = subprocess.check_output(['pbt', 'deploy', '--user-profile',  qgis_profile,  '-y'])

    # Extract deploy path
    outputList = run_pb_tool.split(b'\n')
    deployPath = ([line for line in outputList if b'Deploying to ' in line])[0].split(b' ')[-1]

    plugin_dir = deployPath.decode('utf-8')
    zip_file = os.path.join(os.path.dirname(plugin_dir), PKG_NAME + '.zip')

    # Zip content of deployed plugin
    create_zip(zip_file, plugin_dir, ZIP_EXCLUDES)
    
    # Now remove deployed plugin folder and extract zip file to have the
    #  final "cleaned up" version
    rmtree(plugin_dir)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(plugin_dir))
