"""
Main Streamlit Application
Orquestador principal de la interfaz GMAT + Porkchop.

Este archivo configura la aplicación, gestiona el estado global (session_state)
y coordina las diferentes pestañas de la interfaz.

Ejecución:
    streamlit run main_app.py
"""

import streamlit as st
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar los módulos de la aplicación
try:
    from setup_outputs import check_and_setup_if_needed
    from porkchop_manager import PorkchopManager
    from gui_components import (
        render_porkchop_tab,
        render_interplanetary_mission_tab,
        render_about_tab
    )
    from config import (
        GMAT_SCRIPT_HELIOCENTRIC,
        GMAT_SCRIPT_TRANSFER,
        GMAT_INSTALL_PATH,
        PORKCHOP_DATA_FILE,
        SIDEBAR_LOGO
    )
except ImportError as e:
    st.error(f"❌ Error al importar módulos: {str(e)}")
    st.stop()


# ============================================================================
# CONFIGURACIÓN INICIAL - PRIMERA INSTALACIÓN
# ============================================================================

# Verificar y configurar la carpeta Outputs (solo primera vez)
try:
    setup_success = check_and_setup_if_needed()
    if not setup_success:
        st.warning("⚠️ Hubo problemas al configurar la carpeta Outputs. Revisa los logs.")
except Exception as e:
    st.error(f"❌ Error en la configuración inicial: {str(e)}")
    logger.error(f"Error en setup_outputs: {e}", exc_info=True)


# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="GMAT + Porkchop Plot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CONFIGURACIÓN DE RUTAS Y ARCHIVOS
# ============================================================================

# Directorio base de la aplicación (resolve() convierte a ruta absoluta)
APP_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = APP_DIR.parent

# Logo opcional de la barra lateral
SIDEBAR_LOGO_PATH = (APP_DIR / SIDEBAR_LOGO).resolve() if SIDEBAR_LOGO else None

# Archivos de datos y scripts (ajustar según tu estructura)
# Usar resolve() para obtener rutas absolutas
PORKCHOP_DATA_FILE_PATH = (PROJECT_DIR / PORKCHOP_DATA_FILE).resolve()
GMAT_SCRIPT_HELIO_PATH = (PROJECT_DIR / GMAT_SCRIPT_HELIOCENTRIC).resolve()
GMAT_SCRIPT_TRANSFER_PATH = (PROJECT_DIR / GMAT_SCRIPT_TRANSFER).resolve()

# Legacy - para compatibilidad con código antiguo
GMAT_SCRIPT_FILE = GMAT_SCRIPT_HELIO_PATH

# Log de las rutas para debug
logger.info(f"APP_DIR: {APP_DIR}")
logger.info(f"PROJECT_DIR: {PROJECT_DIR}")
logger.info(f"PORKCHOP_DATA_FILE: {PORKCHOP_DATA_FILE_PATH}")
logger.info(f"GMAT_SCRIPT_HELIO: {GMAT_SCRIPT_HELIO_PATH}")
logger.info(f"GMAT_SCRIPT_TRANSFER: {GMAT_SCRIPT_TRANSFER_PATH}")


# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

def initialize_session_state():
    """Inicializa las variables de estado de la sesión."""
    
    # Estado general
    if 'initialized' not in st.session_state:
        st.session_state['initialized'] = True
        st.session_state['gmat_epoch_mjd'] = None
        st.session_state['gmat_flight_time'] = None
        logger.info("Session state inicializado")


# ============================================================================
# CARGA DE MANAGERS (CON CACHÉ porque gmat es lento de pelotas, con los 
# @st.cache_resource evitamos que se lance de cero cada vez)
# ============================================================================

@st.cache_resource
def load_porkchop_manager(data_file: str):
    """
    Carga el manager de Porkchop (cached para evitar recargas).
    
    Args:
        data_file: Ruta al archivo de datos
        
    Returns:
        Instancia de PorkchopManager o None si falla
    """
    try:
        if not os.path.exists(data_file):
            st.warning(f"⚠️ No se encuentra el archivo de datos: {data_file}")
            return None
        
        manager = PorkchopManager(data_file)
        logger.info(f"✅ PorkchopManager cargado desde {data_file}")
        return manager
        
    except Exception as e:
        st.error(f"❌ Error al cargar PorkchopManager: {str(e)}")
        logger.error(f"Error en load_porkchop_manager: {e}", exc_info=True)
        return None


# ============================================================================
# SIDEBAR - INFORMACIÓN Y CONFIGURACIÓN
# ============================================================================

def render_sidebar():
    """Renderiza la barra lateral con información y configuración."""
    
    with st.sidebar:
        if SIDEBAR_LOGO_PATH and SIDEBAR_LOGO_PATH.exists():
            # Logo un poco más grande pero dentro del ancho cómodo de la sidebar
            st.image(str(SIDEBAR_LOGO_PATH), width=200)
        st.title("🚀 GMAT + Porkchop")
        st.markdown("---")
        
        st.subheader("📁 Archivos de Configuración")
        
        # Verificar archivos
        porkchop_exists = PORKCHOP_DATA_FILE_PATH.exists() if PORKCHOP_DATA_FILE_PATH else False
        helio_exists = GMAT_SCRIPT_HELIO_PATH.exists()
        transfer_exists = GMAT_SCRIPT_TRANSFER_PATH.exists()
        gmat_installed = os.path.exists(GMAT_INSTALL_PATH)
        
        st.markdown(f"""
        **Datos Porkchop:**  
        {':white_check_mark:' if porkchop_exists else ':x:'} `{PORKCHOP_DATA_FILE_PATH.name if PORKCHOP_DATA_FILE_PATH else 'N/A'}`  
        <small style="color: gray;">{PORKCHOP_DATA_FILE_PATH.parent if PORKCHOP_DATA_FILE_PATH else ''}</small>
        
        **Script Heliocéntrico:**  
        {':white_check_mark:' if helio_exists else ':x:'} `{GMAT_SCRIPT_HELIO_PATH.name}`  
        <small style="color: gray;">{GMAT_SCRIPT_HELIO_PATH.parent}</small>
        
        **Script Transferencia:**  
        {':white_check_mark:' if transfer_exists else ':x:'} `{GMAT_SCRIPT_TRANSFER_PATH.name}`  
        <small style="color: gray;">{GMAT_SCRIPT_TRANSFER_PATH.parent}</small>
        
        **GMAT Instalado:**  
        {':white_check_mark:' if gmat_installed else ':x:'} `{GMAT_INSTALL_PATH}`
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Información de estado
        st.subheader("📊 Estado de la Sesión")
        
        # Verificar si hay datos de Porkchop para Misión Interplanetaria
        if st.session_state.get('ity_data_from_porkchop', False):
            st.info("📥 Datos recibidos del Porkchop")
            
            readable_date = st.session_state.get('ity_epoch_readable', 'N/A')
            epoch_value = st.session_state.get('ity_epoch_mjd')
            flight_time_value = st.session_state.get('ity_flight_duration')
            
            if epoch_value is not None:
                st.success(f"📅 {readable_date}")
                st.caption(f"MJD: {epoch_value:.3f}")
            
            if flight_time_value is not None:
                st.success(f"⏱️ Duración: {flight_time_value:.1f} días")
        else:
            # Datos legacy de GMAT tab (por compatibilidad)
            epoch_value = st.session_state.get('gmat_epoch_mjd')
            if epoch_value is not None:
                st.success(f"Época GMAT: MJD {epoch_value:.3f}")
            else:
                st.info("Sin datos de misión seleccionados")
            
            flight_time_value = st.session_state.get('gmat_flight_time')
            if flight_time_value is not None:
                st.success(f"Tiempo de vuelo: {flight_time_value:.1f} días")
        
        st.markdown("---")
        
        # Botones de control
        st.subheader("🔧 Controles")
        
        if st.button("🔄 Reiniciar Aplicación"):
            st.cache_resource.clear()
            st.session_state.clear()
            st.rerun()
        
        # Botón para reconfigurar rutas de Outputs (por si el usuario movió la carpeta)
        if st.button("🛠️ Reconfigurar Outputs"):
            from setup_outputs import force_reconfigure
            with st.spinner("Reconfigurando rutas..."):
                success = force_reconfigure()
                if success:
                    st.success("✅ Rutas actualizadas correctamente")
                    st.info("💡 Reinicia la aplicación para aplicar cambios")
                else:
                    st.error("❌ Error al reconfigurar. Revisa los logs.")
        
        st.markdown("---")
        st.caption("Versión MVP 1.0")
        st.caption("Python 3.12 + GMAT R2025a")


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Función principal de la aplicación."""
    
    # Inicializar estado
    initialize_session_state()
    
    # Renderizar sidebar
    render_sidebar()
    
    # Título principal
    st.title("🛰️ GMAT + Porkchop Plot - Análisis de Trayectorias Interplanetarias")
    
    st.markdown("""
    Bienvenido a la interfaz integrada para análisis y refinamiento de trayectorias espaciales.
    Esta herramienta combina la visualización de diagramas Porkchop con la precisión de GMAT R2025a.
    """)
    
    # ========================================================================
    # CARGAR MANAGERS
    # ========================================================================
    
    # Cargar Porkchop Manager (opcional)
    porkchop_manager = None
    if PORKCHOP_DATA_FILE_PATH and PORKCHOP_DATA_FILE_PATH.exists():
        porkchop_manager = load_porkchop_manager(str(PORKCHOP_DATA_FILE_PATH))
    
    # ========================================================================
    # PESTAÑAS PRINCIPALES
    # ========================================================================
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Diagrama Porkchop",
        "🚀 Misión Marte-Tierra",
        "ℹ️ Acerca de"
    ])
    
    with tab1:
        if porkchop_manager is not None:
            render_porkchop_tab(porkchop_manager)
        else:
            st.warning(f"""
            ⚠️ No se pudo cargar el módulo Porkchop.
            
            **Posibles causas:**
            - El archivo de datos no existe: `{PORKCHOP_DATA_FILE}`
            - El formato del archivo es incorrecto
            - Falta una librería requerida (pandas, matplotlib, scipy)
            
            **Solución:**
            - Verifica que el archivo exists
            - Revisa los logs en la consola/terminal
            
            **Nota:** La pestaña de Misión Marte-Tierra puede funcionar independientemente.
            """)
    
    with tab2:
        # Pestaña de Misión Interplanetaria
        render_interplanetary_mission_tab(
            script_helio_path=str(GMAT_SCRIPT_HELIO_PATH),
            script_transfer_path=str(GMAT_SCRIPT_TRANSFER_PATH)
        )
    
    with tab3:
        render_about_tab()
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.caption("Desarrollado con Streamlit 🎈 | GMAT R2025a 🛰️ | Python 3.12 🐍")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Error crítico en la aplicación: {str(e)}")
        logger.error(f"Error crítico: {e}", exc_info=True)
        
        with st.expander("🐛 Debug Info"):
            st.code(f"{type(e).__name__}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
