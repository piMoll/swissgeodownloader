# build

### 1. Update changelog

### 2. Change version information --> Version format: x.y.z
metadata.txt: Change version


### 3. Check if build configs are still up to date
1. pb_tool.cfg
2. build.py


### 4. Add git tag with new version


### 5. Run plugin builder tool to copy plugin to other QGIS profile
```pbt deploy --user-profile pi -y```


### 6. Run build script to create zip file and exclude all unnecessary files
```python build.py```


### 7. Merge dev into master


### 8. Create release on github
1. Title: Swiss Geo Downloader vx.y.z
2. Text: Add change log
3. Assets: Add swissgeodownloader.zip file


### 9. Upload to QGIS plugin repository
