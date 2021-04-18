import requests
from qgis.core import QgsCoordinateReferenceSystem

MAPPER = {

}
BASEURL = 'https://data.geo.admin.ch/api/stac/v0.9/collections'
BBOX = '7.43,46.95,7.44,46.96'

"https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items?bbox=7.43,46.95,7.44,46.96"

def getDatasetList():
    datasetList = {}
    collection = call(BASEURL)
    
    if isinstance(collection, dict) and 'collections' in collection:
        for ds in collection['collections']:
            options = {}
            for sumName, sumItem in ds['summaries'].items():
                if sumName == 'geoadmin:variant':
                    options['format'] = sumItem
                elif sumName == 'eo:gsd':
                    options['resolution'] = [str(r) for r in sumItem]
                elif sumName == 'proj:epsg':
                    coordSysList = []
                    for epsg in sumItem:
                        coordSys = QgsCoordinateReferenceSystem(f'EPSG:{epsg}')
                        coordSysList.append(coordSys.userFriendlyIdentifier())
                        # coordSys.description()
                    options['coordsys'] = coordSysList
            ds['options'] = options
            datasetList[ds['id']] = ds
        
    return datasetList

def getFileList(dataset, bbox, params):
    params = {
        'bbox': ','.join([str(ext) for ext in bbox]),
        **params
    }
    url = ''
    for link in dataset['links']:
        if link['rel'] == 'items':
            url = link['href']
            break
    
    items = call(url, params=params)
    
    if isinstance(items, dict) and 'features' in items:
        return items['features']

def downloadFiles():
    pass

def call(url, params=None):
    if params is None:
        params = {}
    params = {
        **params,
        'format': 'json'
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print('timeout')
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        print('too many redirects')
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)
