#
# make sure pyside2-uic is in path or use fullpath
#
UI2PY=pyside6-uic
I18N=pyside6-lupdate
I18NR=pyside6-lrelease

all: Ui_PreferencesDialog.py Ui_ProjectInfoDialog.py Ui_ProjectInfoOkDialog.py Ui_SearchTextDialog.py

Ui_PreferencesDialog.py: PreferencesDialog.ui
	$(UI2PY) PreferencesDialog.ui > Ui_PreferencesDialog.py

Ui_ProjectInfoDialog.py: ProjectInfoDialog.ui
	$(UI2PY) ProjectInfoDialog.ui > Ui_ProjectInfoDialog.py

Ui_ProjectInfoOkDialog.py: ProjectInfoOkDialog.ui
	$(UI2PY) ProjectInfoOkDialog.ui > Ui_ProjectInfoOkDialog.py

Ui_SearchTextDialog.py: SearchTextDialog.ui
	$(UI2PY) SearchTextDialog.ui > Ui_SearchTextDialog.py

translate:
	$(I18N) -extensions ui . -ts i18n/ui_en.ts  i18n/ui_es.ts

release:
	$(I18NR) i18n/ui_en.ts  i18n/ui_es.ts
	