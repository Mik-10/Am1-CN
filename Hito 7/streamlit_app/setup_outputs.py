"""
Setup de Outputs - Primera Instalación
Configura las rutas de los archivos .script para que apunten a la carpeta Outputs correcta.

Este módulo se ejecuta automáticamente la primera vez que se inicia la aplicación
o cuando se detecta que las rutas en los .script no coinciden con la estructura actual.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================

# Archivo de marca para saber si ya se configuró
SETUP_MARKER_FILE = ".outputs_configured"

# Scripts que necesitan actualización
SCRIPT_FILES = [
    "GMAT_ITY_Heliocentric.script",
    "GMAT_ITY_transfer.script",
    "PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script"
]


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def get_outputs_dir() -> Path:
    """
    Obtiene (y crea si no existe) la carpeta Outputs en el directorio padre de la app.
    
    Returns:
        Path objeto apuntando a la carpeta Outputs
    """
    # Directorio de la app (streamlit_app)
    app_dir = Path(__file__).parent
    
    # Directorio padre (Hito 7)
    parent_dir = app_dir.parent
    
    # Carpeta Outputs
    outputs_dir = parent_dir / "Outputs"
    
    # Crear si no existe
    if not outputs_dir.exists():
        outputs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Carpeta Outputs creada en: {outputs_dir}")
    else:
        logger.info(f"✅ Carpeta Outputs encontrada en: {outputs_dir}")
    
    return outputs_dir


def is_already_configured() -> bool:
    """
    Verifica si ya se ejecutó la configuración inicial.
    
    Returns:
        True si ya está configurado, False si es primera vez
    """
    app_dir = Path(__file__).parent
    marker_file = app_dir / SETUP_MARKER_FILE
    
    return marker_file.exists()


def mark_as_configured():
    """Crea un archivo de marca indicando que ya se configuró."""
    app_dir = Path(__file__).parent
    marker_file = app_dir / SETUP_MARKER_FILE
    
    with open(marker_file, "w") as f:
        f.write("Outputs configured successfully\n")
        f.write(f"Outputs directory: {get_outputs_dir()}\n")
    
    logger.info("✅ Configuración marcada como completada")


def find_report_file_paths(script_content: str) -> List[Tuple[str, str]]:
    """
    Encuentra todas las líneas con .Filename = en el script.
    
    Args:
        script_content: Contenido completo del archivo .script
        
    Returns:
        Lista de tuplas (nombre_report, ruta_completa_actual)
    """
    # Patrón: nombre_report.Filename = 'ruta';
    pattern = r"(\w+)\.Filename\s*=\s*'([^']+)';"
    
    matches = re.findall(pattern, script_content)
    
    return matches


def update_script_paths(script_path: Path, outputs_dir: Path) -> bool:
    """
    Actualiza las rutas de los ReportFile en un archivo .script.
    
    Args:
        script_path: Ruta al archivo .script
        outputs_dir: Ruta a la carpeta Outputs
        
    Returns:
        True si se actualizó correctamente, False si falló
    """
    try:
        # Leer contenido del script
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Encontrar todos los ReportFile.Filename
        report_paths = find_report_file_paths(content)
        
        if not report_paths:
            logger.warning(f"⚠️ No se encontraron ReportFiles en {script_path.name}")
            return False
        
        logger.info(f"📄 Procesando {script_path.name}...")
        logger.info(f"   Encontrados {len(report_paths)} ReportFile(s)")
        
        # Actualizar cada ruta
        for report_name, old_path in report_paths:
            # Extraer solo el nombre del archivo (sin la ruta)
            old_filename = os.path.basename(old_path)
            
            # Construir nueva ruta absoluta
            new_path = outputs_dir / old_filename
            new_path_str = str(new_path).replace('\\', '\\\\')  # Escapar backslashes para GMAT
            
            # Reemplazar en el contenido (mantener formato original con comillas simples)
            old_line = f"{report_name}.Filename = '{old_path}';"
            new_line = f"{report_name}.Filename = '{new_path_str}';"
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                logger.info(f"   ✅ {report_name}: {old_filename}")
            else:
                # Intentar con formato sin escapar (por si acaso)
                old_path_raw = old_path.replace('\\\\', '\\')
                old_line_raw = f"{report_name}.Filename = '{old_path_raw}';"
                
                if old_line_raw in content:
                    content = content.replace(old_line_raw, new_line)
                    logger.info(f"   ✅ {report_name}: {old_filename}")
                else:
                    logger.warning(f"   ⚠️ No se pudo actualizar {report_name}")
        
        # Escribir el contenido actualizado
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"   💾 {script_path.name} actualizado correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al actualizar {script_path.name}: {str(e)}")
        return False


def setup_outputs() -> bool:
    """
    Función principal de configuración.
    Crea la carpeta Outputs y actualiza todos los scripts.
    
    Returns:
        True si todo se configuró correctamente, False si hubo errores
    """
    logger.info("=" * 70)
    logger.info("🔧 CONFIGURACIÓN INICIAL - CARPETA OUTPUTS")
    logger.info("=" * 70)
    
    try:
        # 1. Obtener/crear carpeta Outputs
        outputs_dir = get_outputs_dir()
        logger.info(f"\n📁 Carpeta Outputs: {outputs_dir}")
        
        # 2. Obtener directorio padre (donde están los .script)
        parent_dir = Path(__file__).parent.parent
        
        # 3. Actualizar cada script
        logger.info("\n📝 Actualizando archivos .script...")
        
        all_success = True
        for script_name in SCRIPT_FILES:
            script_path = parent_dir / script_name
            
            if not script_path.exists():
                logger.warning(f"⚠️ Script no encontrado: {script_name}")
                continue
            
            success = update_script_paths(script_path, outputs_dir)
            if not success:
                all_success = False
        
        # 4. Marcar como configurado
        if all_success:
            mark_as_configured()
            logger.info("\n" + "=" * 70)
            logger.info("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
            logger.info("=" * 70)
        else:
            logger.warning("\n" + "=" * 70)
            logger.warning("⚠️ CONFIGURACIÓN COMPLETADA CON ADVERTENCIAS")
            logger.warning("=" * 70)
        
        return all_success
        
    except Exception as e:
        logger.error(f"\n❌ Error durante la configuración: {str(e)}")
        logger.error("=" * 70)
        return False


def check_and_setup_if_needed() -> bool:
    """
    Verifica si es necesario configurar y lo hace si corresponde.
    Esta función se debe llamar al inicio de la aplicación.
    
    Returns:
        True si está configurado (ya estaba o se configuró ahora), False si falló
    """
    if is_already_configured():
        logger.info("✅ Outputs ya configurados previamente")
        # Verificar que la carpeta todavía existe
        outputs_dir = get_outputs_dir()
        if outputs_dir.exists():
            return True
        else:
            logger.warning("⚠️ Carpeta Outputs fue eliminada, reconfigurando...")
            # Eliminar marca y reconfigurar
            app_dir = Path(__file__).parent
            marker_file = app_dir / SETUP_MARKER_FILE
            if marker_file.exists():
                marker_file.unlink()
            return setup_outputs()
    else:
        logger.info("🆕 Primera instalación detectada, configurando...")
        return setup_outputs()


def force_reconfigure():
    """
    Fuerza una reconfiguración eliminando el archivo de marca.
    Útil si el usuario movió la carpeta o necesita resetear.
    """
    app_dir = Path(__file__).parent
    marker_file = app_dir / SETUP_MARKER_FILE
    
    if marker_file.exists():
        marker_file.unlink()
        logger.info("🔄 Marca de configuración eliminada")
    
    return setup_outputs()


# ============================================================================
# EJEMPLO DE USO / TESTING
# ============================================================================

if __name__ == "__main__":
    # Configurar logging para testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    # Ejecutar configuración
    success = check_and_setup_if_needed()
    
    if success:
        print("\n✅ Todo listo para usar la aplicación")
    else:
        print("\n❌ Hubo problemas en la configuración")
