@echo off
REM ============================================================================
REM EJECUTAR APLICACIÓN STREAMLIT - GMAT + Porkchop
REM ============================================================================
REM Este script ejecuta la aplicación Streamlit con Python 3.12
REM Alternativa al script .ps1 si hay problemas con PowerShell
REM ============================================================================

echo ============================================
echo   GMAT + Porkchop Streamlit App
echo   Python 3.12 + GMAT R2025a
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando entorno virtual...
if not exist "venv\Scripts\python.exe" (
    echo ERROR: No se encuentra el entorno virtual
    echo.
    echo Solucion: Crea el entorno virtual primero:
    echo    python -m venv venv
    echo    venv\Scripts\activate.bat
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo       OK - Entorno virtual encontrado
echo.

echo [2/3] Verificando Python 3.12...
venv\Scripts\python.exe --version
echo.

echo [3/3] Iniciando aplicación Streamlit...
echo.
echo ============================================
echo   La aplicación se abrirá en tu navegador
echo   URL: http://localhost:8501
echo.
echo   Presiona Ctrl+C para detener el servidor
echo ============================================
echo.

venv\Scripts\streamlit.exe run main_app.py
