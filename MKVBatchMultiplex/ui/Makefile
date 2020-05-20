#
# make sure pyside2-uic is in path or use fullpath
#
UI2PY=pyside2-uic
I18N=pyside2-lupdate

all: Ui_PreferencesDialog.py 

Ui_PreferencesDialog.py: PreferencesDialog.ui
	$(UI2PY) PreferencesDialog.ui > Ui_PreferencesDialog.py

en_US.ts: PreferencesDialog.ui
	$(I18N) -verbose PreferencesDialog.ui -ts en_US.ts

es_ES.ts: PreferencesDialog.ui
	$(I18N) -verbose PreferencesDialog.ui -ts es_ES.ts
