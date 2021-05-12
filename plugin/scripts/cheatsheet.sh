# execute everything in plugin/

# Compile gui
 pyuic5 ui/sgd_dockwidget_base.ui -o ui/sgd_dockwidget_base.py

# get new translation texts
bash scripts/update-strings.sh en de

# compile translations
bash scripts/compile-strings.sh lrelease en de
