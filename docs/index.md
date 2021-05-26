_For german version see bellow._

## About
The Swiss Geo Downloader allows you to download Swiss geodata in an easy and convenient way. 
Just select a topic, specify the data options and define the download extent. 
The plugin requests files, downloads and adds them as layers to QGIS.

Currently, the plugin provides access to some of the most requested 
swisstopo topics like the precise height model [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html) 
or the [national maps](https://www.swisstopo.admin.ch/de/geodata/maps/smr/smr25.html). 
Additional swisstopo data and further providers will be added in future releases.

The provided datasets are open data and are requested through a [swisstopo API](https://www.geo.admin.ch/de/geo-dienstleistungen/geodienste/downloadienste/stac-api.html#datasets).

If you want to know more about freely available swisstopo geodata, visit [swisstopo - General information on obtaining geodata](https://www.swisstopo.admin.ch/de/geodata/info.html).

## Download
The Plugin is published in the official QGIS Plugin Repository. 
Download it directly from the QGIS plugin manager by searching for _Swiss Geo Downloader_.

## Usage
The plugin lets you select from around a dozen swisstopo datasets. 
After you select one, you can choose from different options like data type or resolution (depending on the selected dataset). 

Also, you can choose for which extent you would like to recieve data. 
The extent can be set to the current map extent or from another layer.

By clicking on the button _Get file list_ you recieve all relevant files. 
Files can be selected and deselected before starting the download. 

If the files are not zipped, they are added automatically to QGIS.


## Further development
The Swiss Geo Downloader isn't finished yet. Here is a list of possible features that could be implemented next:
* Display the bounding box of all files in the map
* Add more swisstopo datasets to the dataset list
* Add other data providers and their datasets to the list
* Make dataset list searchable
* Provide meta data for every dataset



------------------------------------------------------


## Übersicht
Der Swiss Geo Downloader erlaubt es Schweizer Geodaten bequem und einfach in QGIS herunterzuladen. 
Aus einer Liste können diverse Datensätze ausgewählt, deren Eigenschaften angepasst und die Ausdehnung eingeschränkt werden.
Das Plugin zeigt alle passenden Dateien an, lädt sie herunter und fügt sie als Layer zu QGIS hinzu.

Momentan stehen einige der meistgefragten Geodaten der swisstopo wie 
zum Beispiel das hochgenaue Höhenmodell [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html) 
oder die [Landeskarten](https://www.swisstopo.admin.ch/de/geodata/maps/smr/smr25.html) zur Verfügung.
Weitere Datensätze der swisstopo und andere Datenanbieter werden in zukünftigen Versionen ergänzt.

Bei allen Datensätzen handelt es sich um frei verfügbare Geodaten, 
die über eine [swisstopo-API](https://www.geo.admin.ch/de/geo-dienstleistungen/geodienste/downloadienste/stac-api.html#datasets) abgefragt werden.

Falls Sie mehr Informationen zu frei verfügbaren swisstopo Geodaten suchen, finden Sie diese auf: [swisstopo - Allgemeine Informationen zum Bezug der Geodaten](https://www.swisstopo.admin.ch/de/geodata/info.html).


## Download
Das Plugin ist im offiziellen QGIS Plugin Verzeichnis registriert.
Es ist im Plugin Manager als _Swiss Geo Downloader_ aufgelistet und kann dort direkt heruntergeladen werden.

## Verwendung
Das Plugin stellt etwa ein Dutzend swisstopo Datensätze zur Auswahl.
Abhängig vom ausgewählten Datensatz können verschiedene Eigenschaften wie der Dateityp oder die Auflösung angepasst werden.

Zudem kann die Ausdehnung der gewünschten Daten eingeschränkt werden, beispielsweise auf den aktuellen Kartenausschnitt oder einen anderen Layer.

Per Lick auf _Liste anfordern_ wird eine Liste aller zutreffenden Dateien angezeigt. 
Dateien können selektiert oder deselektiert bevor der Download gestartet wird. 
Geodaten, die nicht gezippt sind, werden nach dem Download automatisch als Layer in QGIS hinzugefügt.


## Weiterentwicklung
Der Swiss Geo Downloader wird weiterentwickelt. Folgende Features sind momentan in Planung:
* Ausdehnung der einzelnen Dateien in Karte darstellen
* Mehr swisstopo Datensätze ergänzen
* Datensätze von anderen Datenanbieter ergänzen
* Liste der Datensätze durchsuchbar machen
* Metadaten der Datensätze anzeigen
