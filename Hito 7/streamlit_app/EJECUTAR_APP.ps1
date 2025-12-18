# ============================================================================
# EJECUTAR APLICACIÓN STREAMLIT - GMAT + Porkchop
# ============================================================================
# Este script ejecuta la aplicación Streamlit con Python 3.12
# 
# Requisitos previos:
# 1. Python 3.12 instalado
# 2. Entorno virtual creado (.\venv)
# 3. Dependencias instaladas (pip install -r requirements.txt)
#
# USO: Ejecuta este script desde PowerShell
# ============================================================================

# Definir colores para mensajes
$verde = "Green"
$amarillo = "Yellow"
$rojo = "Red"
$azul = "Cyan"

Write-Host "============================================" -ForegroundColor $azul
Write-Host "  GMAT + Porkchop Streamlit App" -ForegroundColor $azul
Write-Host "  Python 3.12 + GMAT R2025a" -ForegroundColor $azul
Write-Host "============================================" -ForegroundColor $azul
Write-Host ""

# Verificar que estamos en el directorio correcto
$scriptDir = $PSScriptRoot
Set-Location $scriptDir

Write-Host "[1/5] Verificando directorio de trabajo..." -ForegroundColor $amarillo
Write-Host "      Directorio actual: $scriptDir" -ForegroundColor Gray
Write-Host ""

# Verificar que existe el entorno virtual
$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
$venvStreamlit = Join-Path $scriptDir "venv\Scripts\streamlit.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "❌ ERROR: No se encuentra el entorno virtual" -ForegroundColor $rojo
    Write-Host ""
    Write-Host "Solución: Crea el entorno virtual primero:" -ForegroundColor $amarillo
    Write-Host "    python -m venv venv" -ForegroundColor Gray
    Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "    pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "[2/5] Verificando Python 3.12..." -ForegroundColor $amarillo
$pythonVersion = & $venvPython --version 2>&1
Write-Host "      $pythonVersion" -ForegroundColor $verde

if ($pythonVersion -notmatch "3\.12") {
    Write-Host "⚠️  ADVERTENCIA: Se esperaba Python 3.12" -ForegroundColor $amarillo
    Write-Host "    Versión detectada: $pythonVersion" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "[3/5] Verificando instalación de Streamlit..." -ForegroundColor $amarillo
if (-not (Test-Path $venvStreamlit)) {
    Write-Host "❌ ERROR: Streamlit no está instalado" -ForegroundColor $rojo
    Write-Host ""
    Write-Host "Solución: Instala las dependencias:" -ForegroundColor $amarillo
    Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "    pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

$streamlitVersion = & $venvPython -m streamlit --version 2>&1
Write-Host "      $streamlitVersion" -ForegroundColor $verde
Write-Host ""

Write-Host "[4/5] Verificando archivos de datos..." -ForegroundColor $amarillo
$porkchopFile = Join-Path (Split-Path $scriptDir) "DELTA_V_PORKCHOP.txt"
$gmatScript = Join-Path (Split-Path $scriptDir) "Assignment2Test1.script"

if (Test-Path $porkchopFile) {
    Write-Host "      ✓ DELTA_V_PORKCHOP.txt" -ForegroundColor $verde
} else {
    Write-Host "      ⚠️  DELTA_V_PORKCHOP.txt NO ENCONTRADO" -ForegroundColor $amarillo
}

if (Test-Path $gmatScript) {
    Write-Host "      ✓ Assignment2Test1.script" -ForegroundColor $verde
} else {
    Write-Host "      ⚠️  Assignment2Test1.script NO ENCONTRADO" -ForegroundColor $amarillo
}

$gmatPath = "C:\Users\mikde\GMAT_R2025a"
if (Test-Path $gmatPath) {
    Write-Host "      ✓ GMAT R2025a instalado" -ForegroundColor $verde
} else {
    Write-Host "      ⚠️  GMAT R2025a NO ENCONTRADO" -ForegroundColor $amarillo
}
Write-Host ""

Write-Host "[5/5] Iniciando aplicación Streamlit..." -ForegroundColor $amarillo
Write-Host ""
Write-Host "============================================" -ForegroundColor $azul
Write-Host "  La aplicación se abrirá en tu navegador" -ForegroundColor $azul
Write-Host "  URL: http://localhost:8501" -ForegroundColor $azul
Write-Host ""
Write-Host "  Presiona Ctrl+C para detener el servidor" -ForegroundColor $azul
Write-Host "============================================" -ForegroundColor $azul
Write-Host ""

# Ejecutar streamlit
& $venvStreamlit run main_app.py
