_For German version see below._

## About
Swiss Geo Downloader allows you to download Swiss geodata in an easy and convenient way. 
Search datasets, request files, filter by different file properties and add the files to the QGIS map.

Currently, the plugin provides access to a wide range of geodata from Swisstopo and other federal offices. 
For example the precise height model [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html) 
or the [national maps](https://www.swisstopo.admin.ch/de/geodata/maps/smr/smr25.html).

The provided datasets are open data and are requested through the [Swisstopo STAC API](https://www.geo.admin.ch/de/geo-dienstleistungen/geodienste/downloadienste/stac-api.html#datasets).
If you want to know more about freely available Swiss geodata, visit [swisstopo - General information on obtaining geodata](https://www.swisstopo.admin.ch/de/geodata/info.html).

## Download
The Plugin is published in the official QGIS Plugin Repository. 
Download it directly from the QGIS plugin manager by searching for _Swiss Geo Downloader_. 
Make sure to activate the option to check for updates so you receive new versions right away.

## Usage
The plugin lets you search through a wide range of datasets. 
Search terms are compared to the layer ID, title and additional description texts (not visible in the list).

Most datasets consist of only one file. 
After you select the dataset in the list, the file is displayed in the bottom part of the plugin and ready for download.

If a dataset contains multiple files, you first need to specify the extent for which files should be requested.
The extent can be set to the current map extent (default) or read out from another layer.

By clicking on the button _Get file list_ a list of all relevant files will be generated. 
If a dataset contains multiple files, you first need to specify the extent for which files should be requested.
The extent can be set to the current map extent (default) or read out from another layer.

By clicking on the button _Get file list_ you receive all files in the selected extent. 
Filters for file type, timestamp and other properties let you further narrow down your selection. 
Files can be selected and deselected before starting the download. 

If the files are not zipped, they are added automatically to QGIS.


## Further development
The Swiss Geo Downloader isn't finished, yet. Here is a list of possible features that could be implemented next:
* Add other data providers and their datasets to the list
* Make it possible to add cloud-optimized tiffs to QGIS
* Italian translation

Visit the [changelog](https://github.com/piMoll/swissgeodownloader/blob/main/CHANGELOG.md) for a list of past features and fixes.

------------------------------------------------------


## ??bersicht
Der Swiss Geo Downloader erlaubt es, Schweizer Geodaten bequem und einfach in QGIS herunterzuladen.  
Durchsuchen Sie Datens??tze, fordern sie Dateien f??r einen ausgew??hlten Kartenausschnitt an, 
filtern Sie das Ergebnis und f??gen Sie die Geodaten zur QGIS Karte hinzu.

Momentan bietet das Plugin Zugriff auf ein grosse Auswahl von Geodaten der Swisstopo und andere Bundes??mter an.
Beispielswiese das hochgenaue H??henmodell [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html)
oder die [Landeskarten](https://www.swisstopo.admin.ch/de/geodata/maps/smr/smr25.html). 
Weitere Datenanbieter werden in zuk??nftigen Versionen erg??nzt.

Bei allen Datens??tzen handelt es sich um frei verf??gbare Geodaten, 
die ??ber die [Swisstopo STAC API](https://www.geo.admin.ch/de/geo-dienstleistungen/geodienste/downloadienste/stac-api.html#datasets) abgefragt werden.
Falls Sie mehr Informationen zu frei verf??gbaren Schweizer Geodaten suchen, finden Sie diese auf: [Swisstopo - Allgemeine Informationen zum Bezug der Geodaten](https://www.swisstopo.admin.ch/de/geodata/info.html).

## Download
Das Plugin ist im offiziellen QGIS Plugin Verzeichnis verf??gbar.
Es ist im Plugin Manager als _Swiss Geo Downloader_ aufgelistet und kann dort direkt heruntergeladen werden.
Aktivieren Sie die automatische ??berpr??fung auf Aktualisierungen um sofort ??ber neue Versionen informiert zu werden.

## Verwendung
Das Plugin stellt eine grosse Auswahl an Datens??tzen zur Verf??gung. 
??ber das Suchfeld k??nnen ID, Titel und ein Beschreibungstext (in Tabelle nicht sichtbar) durchsucht werden.

Die meisten Datens??tze bestehen aus einer einzelnen Datei.
Beim Klick auf den Datensatz wird die Datei im unteren Teil des Plugins aufgelistet und ist bereit f??r den Download.

Falls der Datensatz aus vielen Einzeldateien besteht, muss zuerst die gew??nschte Ausdehnung der Daten festgelegt werden bevor Dateien aufgelistet werden.
Die Ausdehnung kann ??ber den aktuell ausgew??hlten Kartenausschnitt definiert werden (Standardfall) oder von einem anderen QGIS-Layer ausgelesen werden.

Per Klick auf _Dateiliste anfordern_ wird eine Liste aller zutreffenden Dateien angezeigt. 
??ber verschiedene Filter kann der gew??nschte Dateityp, der Zeitstand und weitere Eigenschaften ausgew??hlt werden.
Dateien k??nnen selektiert oder deselektiert werden, bevor die Auswahl heruntergeladen wird. 

Geodaten, die nicht gezippt sind, werden nach dem Download automatisch als Layer in QGIS hinzugef??gt.


## Weiterentwicklung
Der Swiss Geo Downloader wird weiterentwickelt. Folgende Features sind momentan in Planung:
* Datens??tze von anderen Datenanbieter erg??nzen
* "Cloud-optimized" (gestreamte) Tiffs zu QGIS hinzuf??gen
* Italienische ??bersetzung

Der [Changelog](https://github.com/piMoll/swissgeodownloader/blob/main/CHANGELOG.md) listet bereits umgesetzte Erg??nzungen und Korrekturen auf.
