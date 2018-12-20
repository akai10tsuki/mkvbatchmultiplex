;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;
; mkvBatchMultiplex install script
;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;Include helpful logic library
!include "LogicLib.nsh"

;Include Modern UI
!include "MUI2.nsh"

!define PRODUCT_NAME "mkvBatchMultiplex"
!define PRODUCT_VERSION "0.9.0b1"
!define SETUP_NAME "mkvBatchMultiplex-0.9.0b1.exe"
!define INST_DIR "C:\"

;!define $PROGRAMFILES64
; Installer name
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"

; File to write
OutFile ${SETUP_NAME}

; Default intallation directory
InstallDir "${INST_DIR}mkvBatchMultiplex"

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "SOFTWARE\mkvBatchMultiplex" "Install_Dir"

;ShowInstDetails show
;ShowUnInstDetails show

SetCompressor /SOLID lzma
SetCompressorDictSize 12

;Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "dist\License.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"


;--------------------------------
;Installer Sections

Section "Program Files (Required)" SecProgramFiles

  SectionIn RO

  SetOutPath $INSTDIR

  ; Put files there
  File /r "dist\*.*"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\mkvBatchMultiplex "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\mkvBatchMultiplex" "DisplayName" "NSIS mkvBatchMultiplex"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\mkvBatchMultiplex" \
    "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\mkvBatchMultiplex" "NoModify" 1
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\mkvBatchMultiplex" "NoRepair" 1

SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts" SecShortcuts

  CreateDirectory "$SMPROGRAMS\MKV Batch Multiplex"
  CreateShortcut "$SMPROGRAMS\MKV Batch Multiplex\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortcut "$SMPROGRAMS\MKV Batch Multiplex\mkvBatchMultiplex.lnk" "$INSTDIR\bin\mkvBatchMultiplex.exe" "" \
    "$INSTDIR\bin\mkvBatchMultiplex.exe" 0
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Desktop Shortcut"

  CreateShortcut "$DESKTOP\mkvBatchMultiplex.lnk" "$INSTDIR\bin\mkvBatchMultiplex.exe" "" "$INSTDIR\bin\mkvBatchMultiplex.exe" 0
  
SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecProgramFiles ${LANG_ENGLISH} "Program Files."
  LangString DESC_SecShortcuts ${LANG_ENGLISH} "Start Menu Shortcuts."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecProgramFiles} $(DESC_SecProgramFiles)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} $(DESC_SecShortcuts)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\mkvBatchMultiplex"
  DeleteRegKey HKLM "SOFTWARE\mkvBatchMultiplex"

  ; Delete files
  RMDir /r "$INSTDIR\bin"
  Delete "$INSTDIR\AUTHORS"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\Readme.txt"

  ; Delete shortcuts
  Delete "$DESKTOP\mkvBatchMultiplex.lnk"
  Delete "$SMPROGRAMS\MKV Batch Multiplex\*.*"

  ; Remove shortcuts directory
  RMDir "$SMPROGRAMS\MKV Batch Multiplex"
  
  ; Delete uninstaller
  Delete "$INSTDIR\Uninstall.exe"

  ; Delete install directory
  RMDir "$INSTDIR"
  
SectionEnd

