@echo off
setlocal

:: This script creates a release bundle for SearchEPG.
:: It takes one argument: the destination path.

if "%~1"=="" (
    echo Usage: create_release.cmd ^<destination_path^>
    exit /b 1
)

set "DEST_DIR=%~1"
set "ROOT_DIR=%~dp0..\"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIST_DIR=%ROOT_DIR%frontend\dist"
set "SCRIPTS_DIR=%ROOT_DIR%scripts"

echo --- Creating release bundle in: %DEST_DIR% ---

:: 1. Clean up old release directory
if exist "%DEST_DIR%" (
    echo Removing existing directory: %DEST_DIR%
    rmdir /s /q "%DEST_DIR%"
)

:: 2. Create directories
echo Creating directories...
mkdir "%DEST_DIR%"
mkdir "%DEST_DIR%\data"
mkdir "%DEST_DIR%\plugins"
mkdir "%DEST_DIR%\frontend"

:: 3. Copy application files and directories
echo.
echo --- Copying application files ---

echo Copying backend...
xcopy /e /i /q "%BACKEND_DIR%" "%DEST_DIR%\backend\"

echo Copying frontend distribution...
xcopy /e /i /q "%FRONTEND_DIST_DIR%" "%DEST_DIR%\frontend\dist\"

echo Copying root files...
copy "%ROOT_DIR%app.yaml" "%DEST_DIR%\app.yaml"
copy "%BACKEND_DIR%\requirements.txt" "%DEST_DIR%\requirements.txt"
copy "%BACKEND_DIR%\env.txt" "%DEST_DIR%\.env.example"

:: 4. Copy README.md
echo Copying instruction file...
copy "%SCRIPTS_DIR%\README.md" "%DEST_DIR%\README.md"

echo.
echo --- Release bundle created successfully! ---
echo Folder: %DEST_DIR%

endlocal
