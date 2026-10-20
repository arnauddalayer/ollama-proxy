@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo   Installation des dependances pour ollama-proxy
echo ======================================================

:: Détecte Miniforge dans les deux emplacements possibles
set "MINIFORGE_USER=%LOCALAPPDATA%\miniforge3"
set "MINIFORGE_SYSTEM=%ProgramData%\miniforge3"

:: Vérifie d'abord le répertoire d'utilisateur
if exist "%MINIFORGE_USER%\Scripts\activate.bat" (
    echo [INFO] Detecte Miniforge dans %MINIFORGE_USER%
    call "%MINIFORGE_USER%\Scripts\activate.bat" "%MINIFORGE_USER%"
) else (
    :: Si pas trouvé, vérifie le répertoire system
    if exist "%MINIFORGE_SYSTEM%\Scripts\activate.bat" (
        echo [INFO] Detecte Miniforge dans %MINIFORGE_SYSTEM%
        call "%MINIFORGE_SYSTEM%\Scripts\activate.bat" "%MINIFORGE_SYSTEM%"
    ) else (
        echo [INFO] Miniforge non detecte, utilisation de Python standard.
    )
)

:: conda et mamba sont des gestionnaires de paquets; le venv doit etre cree par Python.
set "PYTHON_EXE=python"

:: Vérification finale de la présence de Python
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas detecte.
    echo Veuillez installer Python ou Miniforge.
    pause
    exit /b
)

echo 1. Creation de l'environnement virtuel (.venv)...
:: Si on utilise conda/mamba, on peut utiliser une commande plus directe
:: Mais pour rester compatible avec la structure existante, on utilise l'exécutable trouvé
if not exist .venv (
    %PYTHON_EXE% -m venv .venv
) else (
    echo L'environnement existe deja.
)

echo 2. Activation et installation des bibliotheques...
:: On utilise "call" pour s'assurer que le script continue apres l'activation
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ======================================================
echo   Installation terminee avec succes !
echo ======================================================
pause
