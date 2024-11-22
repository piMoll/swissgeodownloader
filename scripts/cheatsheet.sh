# execute everything in plugin/

# Compile resources
pyrcc5 -o resources/resources.py resources/resources.qrc

# Compile gui
pyuic6 ui/sgd_dockwidget_base.ui -o ui/sgd_dockwidget_base.py
# patch gui to behave agnostic PyQt v5/6
sed -i -e 's/from PyQt6/from qgis.PyQt/' ui/sgd_dockwidget_base.py

# get new translation texts
bash scripts/update-strings.sh en de fr

# compile translations
bash scripts/compile-strings.sh lrelease en de fr
