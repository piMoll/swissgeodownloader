# Changelog
All notable changes to this project will be documented in this file.

## [1.4] - 2022-03-30
### Added
- Saarch bar for datasets: Looks through datasets names and descriptions
- Options have been replaced with file filters. Only relevant filters are shown depending on the current dataset and extent
- Timestamp filter includes option 'current' and 'all'
- Cancel button for file list requests

### Fixed
- Swissalti3d and other datasets with multiple timestamps only showed oldest and newest timestamp

## [1.3] - 2022-02-02
### Added
- If a dataset contains one single file, the plugin will list this file automatically

### Fixed
- Plugin not working because it cannot process the received list of datasets
- Use API paging to get all datasets instead of first 100
- Improve plugin behaviour when quickly clicking through dataset list

## [1.2] - 2022-01-02
### Added
- French translations, thanks to [romainbh](https://github.com/romainbh)
### Fixed
- Wrongfully added a bounding box as request parameter even though the extent option was deactivated. The resulting file list therefore was often empty.
- The button for extent option 'current layer' was removed because it does not behave consistently.
- The bounding box from option 'calculate from layer' was not read out correctly.

## [1.1] - 2021-09-05
### Added
- Show bounding box of the available files in map
- Added button to refresh dataset list
- Switch automatically to swiss crs if map is empty
- Suggest crs change if user is not in swiss crs 
### Fixed
- Improve API error handling, show correct error response instead of generic ones
- Don't show error message if user cancels a request
- Show full file type in dropdown even if it's in a zip
- Use API paging to get all files instead of first 100
- Check internet connection on initialization and inform user if API cannot be accessed
- GUI improvements for small displays

## [1.0] - 2021-05-26
This is the initial version of the Swiss Data Downloader plugin.
### Added
- Load swisstopo STAC collection content, display the available datasets in a list
- Show dataset options
- Show extent widget to get current map extent or layer extent
- Show available files in a filterable list
- Download files and add them to QGIS
