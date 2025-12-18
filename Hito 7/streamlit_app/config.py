"""
Archivo de Configuración Centralizada
Modifica estos valores según tu instalación y necesidades.
"""

import os
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN DE GMAT
# ============================================================================

# Ruta de instalación de GMAT R2025a
# IMPORTANTE: Evitar tildes, espacios y caracteres especiales
GMAT_INSTALL_PATH = r"C:\\Users\\mikde\\GMAT_R2025a"

# Nombre del archivo de inicio de GMAT API
GMAT_API_STARTUP_FILE = "api_startup_file.txt"

# Nombre del objeto Spacecraft en el script GMAT
GMAT_SPACECRAFT_NAME = "heliocentric_SC"

# Nombre de la variable de tiempo de vuelo en GMAT (si existe)
GMAT_FLIGHT_TIME_VAR = "FlightTime"

# ============================================================================
# CONFIGURACIÓN DE ARCHIVOS DE DATOS
# ============================================================================

# Nombre del archivo de resultados Porkchop (formato definitivo)
PORKCHOP_DATA_FILE = "DELTA_V_PORKCHOP.txt"

# Nombres de los scripts GMAT (sistema de misión interplanetaria)
GMAT_SCRIPT_HELIOCENTRIC = "GMAT_ITY_Heliocentric.script"  # Trayectoria heliocéntrica
GMAT_SCRIPT_TRANSFER = "GMAT_ITY_transfer.script"          # Transferencia completa

# Archivos de salida de GMAT
HYPERBOLIC_VELS_FILE = "hyperbolic_vels.txt"   # Velocidades hiperbólicas
FINAL_RESULTS_FILE = "FinalResults.txt"        # Resultados finales de la misión

# Legacy - mantener para compatibilidad
GMAT_SCRIPT_FILE = GMAT_SCRIPT_HELIOCENTRIC
DELTAV_OUTPUT_FILE = "DeltaV.txt"

# ============================================================================
# CONFIGURACIÓN DE MISIÓN INTERPLANETARIA
# ============================================================================

# Parámetros por defecto para la misión Mars-Earth
MISSION_DEFAULTS = {
    'mission_epoch': '06 Jun 2026 11:59:28.000',
    'flight_duration': 350,  # días
    'sma_dep': 6500,         # km - Semi-major axis departure orbit (Mars)
    'sma_arr': 31780,        # km - Semi-major axis arrival orbit (Earth)
    'inc_dep': 50,           # deg - Inclination departure orbit
    'inc_arr': 80,           # deg - Inclination arrival orbit
    'ecc_dep': 0.00000000001,  # Excentricidad salida (casi circular)
    'ecc_arr': 0.7936,       # Excentricidad llegada
}

# ============================================================================
# CONFIGURACIÓN DE PORKCHOP PLOT
# ============================================================================

# Parámetros por defecto para el diagrama Porkchop
PORKCHOP_DEFAULTS = {
    'deltav_min': 6.0,          # km/s
    'deltav_max': 13.0,         # km/s
    'deltav_step': 0.5,         # km/s
    'tof_levels': [290, 310, 330, 350],  # días
    'figsize': (12, 8),         # pulgadas
}

# Referencia de conversión MJD a fecha gregoriana
# Estos valores se usan para convertir Modified Julian Date a fechas legibles
MJD_REFERENCE = {
    'base_mjd': 31136.999630,
    'base_date': '2026-04-06',  # Formato: YYYY-MM-DD
}

# ============================================================================
# CONFIGURACIÓN DE INTERFAZ STREAMLIT
# ============================================================================

# Configuración de la página
PAGE_CONFIG = {
    'page_title': "GMAT + Porkchop Plot",
    'page_icon': "🚀",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Logo opcional en la barra lateral (ruta relativa a streamlit_app)
# Deja None para no mostrar imagen
SIDEBAR_LOGO = "logo.png"

# Rango de valores permitidos en la GUI
GUI_RANGES = {
    'epoch_mjd': {
        'min': 30000.0,
        'max': 35000.0,
        'default': 31136.99962962963,
    },
    'flight_time': {
        'min': 50.0,
        'max': 500.0,
        'default': 210.0,
    },
    'max_deltav_filter': {
        'min': 5.0,
        'max': 15.0,
        'default': 8.0,
    }
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Nivel de logging
LOGGING_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Archivo de log de GMAT
GMAT_LOG_FILE = "GMAT_Backend_Log.txt"

# Imprimir logs de GMAT en consola
GMAT_ECHO_TO_CONSOLE = False  # True para ver todo el output de GMAT

# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================

def validate_config():
    """
    Valida que la configuración sea correcta.
    Retorna una lista de warnings si hay problemas.
    """
    warnings = []
    
    # Validar que GMAT existe
    if not os.path.exists(GMAT_INSTALL_PATH):
        warnings.append(f"GMAT no encontrado en: {GMAT_INSTALL_PATH}")
    
    # Validar archivo de startup de GMAT
    startup_file = os.path.join(GMAT_INSTALL_PATH, "bin", GMAT_API_STARTUP_FILE)
    if not os.path.exists(startup_file):
        warnings.append(f"Archivo de startup no encontrado: {startup_file}")
    
    return warnings


# ============================================================================
# UTILIDADES
# ============================================================================

def get_project_root():
    """Retorna la ruta raíz del proyecto."""
    return Path(__file__).parent.parent


def get_data_file_path(filename):
    """
    Retorna la ruta completa a un archivo de datos.
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Path absoluto al archivo
    """
    return get_project_root() / filename


# ============================================================================
# EXPORTAR CONFIGURACIÓN
# ============================================================================

__all__ = [
    'GMAT_INSTALL_PATH',
    'GMAT_API_STARTUP_FILE',
    'GMAT_SPACECRAFT_NAME',
    'GMAT_FLIGHT_TIME_VAR',
    'PORKCHOP_DATA_FILE',
    'GMAT_SCRIPT_FILE',
    'GMAT_SCRIPT_HELIOCENTRIC',
    'GMAT_SCRIPT_TRANSFER',
    'HYPERBOLIC_VELS_FILE',
    'FINAL_RESULTS_FILE',
    'DELTAV_OUTPUT_FILE',
    'MISSION_DEFAULTS',
    'PORKCHOP_DEFAULTS',
    'MJD_REFERENCE',
    'PAGE_CONFIG',
    'GUI_RANGES',
    'LOGGING_LEVEL',
    'GMAT_LOG_FILE',
    'GMAT_ECHO_TO_CONSOLE',
    'validate_config',
    'get_project_root',
    'get_data_file_path',
]
