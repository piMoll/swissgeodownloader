# execute everything in plugin/

# Compile resources
pyrcc5 -o resources/resources.py resources/resources.qrc

# Compile gui
pyuic5 ui/sgd_dockwidget_base.ui -o ui/sgd_dockwidget_base.py

# get new translation texts
bash scripts/update-strings.sh en de fr

# compile translations
bash scripts/compile-strings.sh lrelease en de fr
