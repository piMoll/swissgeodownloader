_For german version see bellow._

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
Make sure to activate the option to check for updates so you recieve new versions right away.

## Usage
The plugin lets you search trough a wide range of datasets. 
Search terms are compared to the layer ID, title and additional description texts (not visible in the list).

Most datasets consist of only one file. 
After you select the dataset in the list, the file is displayed in the bottom part of the plugin and ready for download.

If a dataset contains multiple files, you first need to specify the extent for which files should be requested.
The extent can be set to the current map extent (default) or read out from another layer.

By clicking on the button _Get file list_ you receive all files in the selected extent. 
Filters for file type, timestamp and other properties let you further narrow down your selection. 
Files can be selected and deselected before starting the download. 

If the files are not zipped, they are added automatically to QGIS.


## Further development
The Swiss Geo Downloader isn't finished yet. Here is a list of possible features that could be implemented next:
* Add other data providers and their datasets to the list
* Make it possible to add cloud-optimized tiffs to QGIS
* Italian translation

Visit the [changelog](https://github.com/piMoll/swissgeodownloader/blob/main/CHANGELOG.md) for a list of past features and fixes.

------------------------------------------------------


## Übersicht
Der Swiss Geo Downloader erlaubt es, Schweizer Geodaten bequem und einfach in QGIS herunterzuladen.  
Durchsuchen Sie Datensätze, fordern sie Dateien für einen ausgewählten Kartenausschnitt an, 
filtern Sie das Ergebnis und fügen Sie die Geodaten zur QGIS Karte hinzu.

Momentan bietet das Plugin Zugriff auf ein grosse Auswahl von Geodaten der Swisstopo und andere Bundesämter an.
Beispielswiese das hochgenaue Höhenmodell [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html)
oder die [Landeskarten](https://www.swisstopo.admin.ch/de/geodata/maps/smr/smr25.html). 
Weitere Datenanbieter werden in zukünftigen Versionen ergänzt.

Bei allen Datensätzen handelt es sich um frei verfügbare Geodaten, 
die über die [Swisstopo STAC API](https://www.geo.admin.ch/de/geo-dienstleistungen/geodienste/downloadienste/stac-api.html#datasets) abgefragt werden.
Falls Sie mehr Informationen zu frei verfügbaren Schweizer Geodaten suchen, finden Sie diese auf: [Swisstopo - Allgemeine Informationen zum Bezug der Geodaten](https://www.swisstopo.admin.ch/de/geodata/info.html).

## Download
Das Plugin ist im offiziellen QGIS Plugin Verzeichnis verfügbar.
Es ist im Plugin Manager als _Swiss Geo Downloader_ aufgelistet und kann dort direkt heruntergeladen werden.
Aktivieren Sie die automatische Überprüfung auf Aktualisierungen um sofort über neue Versionen informiert zu werden.

## Verwendung
Das Plugin stellt eine grosse Auswahl an Datensätze zur Verfügung. 
Über das Suchfeld können ID, Titel und ein Beschreibungstext (in Tabelle nicht sichtbar) durchsucht werden.

Die meisten Datensätze bestehen aus einer einzelnen Datei.
Beim Klick auf den Datensatz wird die Datei im unteren Teil des Plugins aufgelistet und ist bereit für den Download.

Falls der Datensatz aus vielen Einzeldateien besteht, muss zuerst die gewünschte Ausdehnung der Daten festgelegt werden bevor Dateien aufgelistet werden.
Die Ausdehnung kann über den aktuell ausgewählten Kartenausschnitt definiert werden (Standardfall) oder von einem anderen QGIS-Layer ausgelesen werden.

Per Kick auf _Dateiliste anfordern_ wird eine Liste aller Dateien im Ausschnitt angefordert. 
Über verschiedene Filter kann der gewünschte Dateityp, der Zeitstand und weitere Eigenschaften ausgewählt werden.
Dateien können selektiert oder deselektiert werden bevor die Auswahl heruntergeladen wird. 

Geodaten, die nicht gezippt sind, werden nach dem Download automatisch als Layer in QGIS hinzugefügt.


## Weiterentwicklung
Der Swiss Geo Downloader wird weiterentwickelt. Folgende Features sind momentan in Planung:
* Datensätze von anderen Datenanbieter ergänzen
* "Cloud-optimized" (gestreamte) Tiffs zu QGIS hinzufügen
* Italienische Übersetzung

Der [Changelog](https://github.com/piMoll/swissgeodownloader/blob/main/CHANGELOG.md) listet bereits umgesetzte Ergänzungen und Korrekturen auf.
