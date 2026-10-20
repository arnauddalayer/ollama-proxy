@echo off
IF "%PROCESSOR_ARCHITEW6432%"=="" GOTO native
%SystemRoot%\Sysnative\cmd.exe /c %0 %*
exit

:native
:: Se placer dans le dossier du script (chemins relatifs : .venv, index.html, config.py)
cd /d "%~dp0"

:: Vérification de l'environnement virtuel
if not exist .venv (
    echo [ERREUR] L'environnement virtuel .venv n'existe pas.
    echo Veuillez executer W_install_requirements.bat pour initialiser l'environnement.
    pause
    exit /b
)

:: Activation de l'environnement virtuel
call .venv\Scripts\activate
if errorlevel 1 (
    echo [ERREUR] Echec de l'activation de l'environnement virtuel.
    pause
    exit /b
)

:: Exécution du script Python
REM en local seulement
uvicorn proxy:app --host 127.0.0.1 --port 11434

REM accessible du réseau local
:: uvicorn proxy:app --host 0.0.0.0 --port 11434

if errorlevel 1 (
    echo [ERREUR] L'execution du script a echoue.
    pause
) else (
    pause
)
