#
# make sure pyside2-uic is in path or use fullpath
#
UI2PY=pyside2-uic
I18N=pyside2-lupdate

all: Ui_PreferencesDialog.py Ui_ProjectInfoDialog.py Ui_ProjectInfoOkDialog.py Ui_SearchTextDialog.py

Ui_PreferencesDialog.py: PreferencesDialog.ui
	$(UI2PY) PreferencesDialog.ui > Ui_PreferencesDialog.py

Ui_ProjectInfoDialog.py: ProjectInfoDialog.ui
	$(UI2PY) ProjectInfoDialog.ui > Ui_ProjectInfoDialog.py

Ui_ProjectInfoOkDialog.py: ProjectInfoOkDialog.ui
	$(UI2PY) ProjectInfoOkDialog.ui > Ui_ProjectInfoOkDialog.py

Ui_SearchTextDialog.py: SearchTextDialog.ui
	$(UI2PY) SearchTextDialog.ui > Ui_SearchTextDialog.py
