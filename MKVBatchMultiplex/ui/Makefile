#
# make sure pyside2-uic is in path or use fullpath
#
UI2PY=pyside2-uic

all: Ui_PreferencesDialog.py

Ui_PreferencesDialog.py: PreferencesDialog.ui
	$(UI2PY) PreferencesDialog.ui > Ui_PreferencesDialog.py
