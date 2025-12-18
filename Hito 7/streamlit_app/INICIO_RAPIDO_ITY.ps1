# =========================================================================
# INICIO RÁPIDO - VERSIÓN INTERPLANETARIA
# Script de PowerShell para configurar y ejecutar la aplicación Interplanetaria
# =========================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  APLICACIÓN INTERPLANETARIA - INICIO RÁPIDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# =========================================================================
# PASO 1: Verificar Python
# =========================================================================

Write-Host "PASO 1: Verificando Python 3.12..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python encontrado: $pythonVersion" -ForegroundColor Green
    
    if ($pythonVersion -notmatch "3\.12") {
        Write-Host "  ⚠ ADVERTENCIA: Se recomienda Python 3.12" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ ERROR: Python no encontrado" -ForegroundColor Red
    Write-Host "  Instala Python 3.12 desde https://www.python.org/" -ForegroundColor Red
    exit 1
}

Write-Host ""

# =========================================================================
# PASO 2: Verificar Scripts GMAT
# =========================================================================

Write-Host "PASO 2: Verificando scripts GMAT..." -ForegroundColor Yellow

$scriptHelio = "..\GMAT_ITY_Heliocentric.script"
$scriptTransfer = "..\GMAT_ITY_transfer.script"

if (Test-Path $scriptHelio) {
    Write-Host "  ✓ GMAT_ITY_Heliocentric.script encontrado" -ForegroundColor Green
} else {
    Write-Host "  ✗ GMAT_ITY_Heliocentric.script NO encontrado" -ForegroundColor Red
    Write-Host "    Ruta esperada: $scriptHelio" -ForegroundColor Red
    $scriptsOk = $false
}

if (Test-Path $scriptTransfer) {
    Write-Host "  ✓ GMAT_ITY_transfer.script encontrado" -ForegroundColor Green
} else {
    Write-Host "  ✗ GMAT_ITY_transfer.script NO encontrado" -ForegroundColor Red
    Write-Host "    Ruta esperada: $scriptTransfer" -ForegroundColor Red
    $scriptsOk = $false
}

if (-not $scriptsOk) {
    Write-Host ""
    Write-Host "  IMPORTANTE: Copia los scripts GMAT al directorio padre" -ForegroundColor Yellow
    Write-Host "  (un nivel arriba de streamlit_app)" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""

# =========================================================================
# PASO 3: Verificar GMAT
# =========================================================================

Write-Host "PASO 3: Verificando instalación de GMAT..." -ForegroundColor Yellow

$gmatPath = "C:\Users\mikde\GMAT_R2025a"
$gmatStartup = "$gmatPath\bin\api_startup_file.txt"

if (Test-Path $gmatPath) {
    Write-Host "  ✓ GMAT encontrado en: $gmatPath" -ForegroundColor Green
} else {
    Write-Host "  ✗ GMAT NO encontrado en: $gmatPath" -ForegroundColor Red
}

if (Test-Path $gmatStartup) {
    Write-Host "  ✓ api_startup_file.txt encontrado" -ForegroundColor Green
} else {
    Write-Host "  ✗ api_startup_file.txt NO encontrado" -ForegroundColor Red
}

Write-Host ""

# =========================================================================
# PASO 4: Verificar Dependencias
# =========================================================================

Write-Host "PASO 4: Verificando dependencias de Python..." -ForegroundColor Yellow

$required = @("streamlit", "numpy", "pandas", "matplotlib", "scipy")
$missing = @()

foreach ($pkg in $required) {
    try {
        $installed = pip show $pkg 2>&1
        if ($installed -match "Name: $pkg") {
            Write-Host "  ✓ $pkg instalado" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $pkg NO instalado" -ForegroundColor Red
            $missing += $pkg
        }
    } catch {
        Write-Host "  ✗ $pkg NO instalado" -ForegroundColor Red
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "  Instalando dependencias faltantes..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""

# =========================================================================
# PASO 5: Verificar Módulos Interplanetarios
# =========================================================================

Write-Host "PASO 5: Verificando módulos interplanetarios..." -ForegroundColor Yellow

$modules = @("ity_mission.py", "gmat_backend_ity.py", "gui_components.py", "main_app.py")

foreach ($mod in $modules) {
    if (Test-Path $mod) {
        Write-Host "  ✓ $mod encontrado" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $mod NO encontrado" -ForegroundColor Red
    }
}

Write-Host ""

# =========================================================================
# PASO 6: Ejecutar Aplicación
# =========================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO APLICACIÓN STREAMLIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "La aplicación se abrirá en tu navegador..." -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Esperar 2 segundos
Start-Sleep -Seconds 2

# Ejecutar Streamlit
streamlit run main_app.py
