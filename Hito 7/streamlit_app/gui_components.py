"""
GUI Components Module
Componentes de interfaz pura para Streamlit.

Cada función renderiza una sección específica de la GUI y maneja
la interacción del usuario con los managers correspondientes.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Optional
import logging
import os

# Importar plotly solo si está disponible
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Plotly no está instalado. La visualización 3D no estará disponible.")

# Importar módulos de misión interplanetaria
try:
    from ity_mission import MissionConfig
    from gmat_backend_ity import InterplanetaryMission, GmatBackendError
except ImportError as e:
    logger.warning(f"⚠️ No se pudieron importar módulos de misión interplanetaria: {e}")

# Configuración de logging
logger = logging.getLogger(__name__)


# ============================================================================
# TAB 1: PORKCHOP DIAGRAM
# ============================================================================

def render_porkchop_tab(porkchop_manager):
    """
    Renderiza la pestaña de visualización del diagrama Porkchop.
    
    Args:
        porkchop_manager: Instancia de PorkchopManager con datos cargados
    """
    st.header("📊 Diagrama Porkchop - Análisis de Trayectorias")
    
    st.markdown("""
    El diagrama Porkchop muestra la relación entre:
    - **Fecha de lanzamiento** (eje X)
    - **Fecha de llegada** (eje Y)
    - **ΔV total requerido** (contornos de color)
    - **Tiempo de vuelo** (líneas rojas diagonales)
    """)
    
    # ========================================================================
    # Controles de configuración
    # ========================================================================
    st.subheader("⚙️ Configuración del Diagrama")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_auto_min = st.checkbox(
            "Calcular mínimo automáticamente",
            value=True,
            help="Usar el valor mínimo de los datos"
        )
        deltav_min = None if use_auto_min else st.number_input(
            "ΔV mínimo (km/s)",
            min_value=0.0,
            max_value=20.0,
            value=6.0,
            step=0.5,
            help="Valor mínimo para los contornos de ΔV"
        )
    
    with col2:
        deltav_max = st.number_input(
            "ΔV máximo (km/s)",
            min_value=0.0,
            max_value=20.0,
            value=13.0,
            step=0.5,
            help="Valor máximo para los contornos de ΔV"
        )
    
    with col3:
        deltav_step = st.number_input(
            "Paso de ΔV (km/s)",
            min_value=0.05,
            max_value=2.0,
            value=0.20,
            step=0.05,
            help="Separación entre contornos (0.20 recomendado para buena resolución)"
        )
    
    # Configuración de líneas de ToF
    st.markdown("**Líneas de Tiempo de Vuelo (ToF)**")
    tof_input = st.text_input(
        "Niveles de ToF (días, separados por comas)",
        value="290, 310, 330, 350, 370",
        help="Ejemplo: 290, 310, 330, 350, 370"
    )
    
    # Parsear los niveles de ToF
    try:
        tof_levels = [int(x.strip()) for x in tof_input.split(',') if x.strip()]
    except ValueError:
        st.warning("⚠️ Formato inválido para ToF. Usando valores por defecto.")
        tof_levels = [290, 310, 330, 350, 370]
    
    # ========================================================================
    # Generar y mostrar el diagrama
    # ========================================================================
    if st.button("🚀 Generar Diagrama Porkchop", type="primary"):
        logger.info("\n\n" + "="*80)
        logger.info("USUARIO: GENERAR DIAGRAMA PORKCHOP")
        logger.info(f"Parámetros: ΔV {deltav_min}-{deltav_max} km/s (step {deltav_step}) | ToF levels: {tof_levels}")
        logger.info("="*80 + "\n")
        
        with st.spinner("📊 Generando diagrama Porkchop... Interpolando datos y creando contornos de ΔV..."):
            try:
                fig = porkchop_manager.get_porkchop_figure(
                    deltav_min=deltav_min,
                    deltav_max=deltav_max,
                    deltav_step=deltav_step,
                    tof_levels=tof_levels,
                    figsize=(10, 5)
                )
                
                # Mostrar la figura en Streamlit
                st.pyplot(fig)
                
                # Cerrar la figura para liberar memoria
                import matplotlib.pyplot as plt
                plt.close(fig)
                
                logger.info("✓ Diagrama generado exitosamente\n" + "="*80 + "\n\n")
                st.success("✅ Diagrama generado exitosamente")
                
            except Exception as e:
                logger.error("❌ ERROR PORKCHOP: " + str(e))
                logger.error("="*80 + "\n\n")
                
                st.error(f"❌ Error al generar el diagrama: {str(e)}")
                logger.error(f"Error en Porkchop: {e}", exc_info=True)
    
    # ========================================================================
    # Análisis de ventanas óptimas
    # ========================================================================
    st.divider()
    st.subheader("🎯 Ventanas de Lanzamiento Óptimas")
    
    max_deltav_filter = st.slider(
        "ΔV máximo aceptable (km/s)",
        min_value=5.0,
        max_value=15.0,
        value=8.0,
        step=0.5,
        help="Filtrar trayectorias por ΔV máximo"
    )
    
    if st.button("🔍 Buscar Ventanas Óptimas"):
        logger.info("\n\n" + "="*80)
        logger.info(f"USUARIO: BUSCAR VENTANAS ÓPTIMAS (ΔV máx: {max_deltav_filter} km/s)")
        logger.info("="*80 + "\n")
        
        with st.spinner("🔍 Analizando datos de trayectorias y buscando ventanas óptimas de lanzamiento..."):
            try:
                optimal_windows = porkchop_manager.get_optimal_launch_window(
                    max_deltav=max_deltav_filter
                )
                
                if len(optimal_windows) > 0:
                    logger.info(f"✓ {len(optimal_windows)} ventanas encontradas | Mejor: MJD {optimal_windows.iloc[0]['Start_MJD']:.3f}, ΔV {optimal_windows.iloc[0]['DeltaV']:.2f} km/s")
                else:
                    logger.info("⚠ No se encontraron ventanas óptimas")
                logger.info("="*80 + "\n\n")
                
                # Guardar en session_state para mantener datos
                st.session_state['optimal_windows'] = optimal_windows
                
            except Exception as e:
                st.error(f"❌ Error al buscar ventanas: {str(e)}")
                logger.error(f"Error en búsqueda de ventanas: {e}", exc_info=True)
    
    # Mostrar ventanas si existen en session_state
    if 'optimal_windows' in st.session_state and len(st.session_state['optimal_windows']) > 0:
        optimal_windows = st.session_state['optimal_windows'].copy()
        
        # Añadir columna con fecha legible
        from datetime import datetime, timedelta
        def mjd_to_readable(mjd, base_mjd=31136.999630, base_date_str='2026-04-06'):
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            target_date = base_date + timedelta(days=float(mjd) - base_mjd)
            return target_date.strftime('%d %b %Y')
        
        optimal_windows['Fecha_Lanzamiento'] = optimal_windows['Start_MJD'].apply(mjd_to_readable)
        
        # Renombrar columnas para mejor visualización
        display_df = optimal_windows[['Fecha_Lanzamiento', 'Start_MJD', 'Duration', 'DeltaV']].head(10).copy()
        display_df.columns = ['Fecha Lanzamiento', 'MJD', 'Duración (días)', 'ΔV (km/s)']
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True
        )
        
        # Permitir seleccionar una fecha para pasarla a la Misión Interplanetaria
        st.markdown("**💡 Selecciona una fecha para la Misión Marte-Tierra:**")
        
        # Valor por defecto: usar el índice guardado o 0
        default_idx = st.session_state.get('selected_window_idx', 0)
        
        selected_idx = st.selectbox(
            "Ventana de lanzamiento:",
            range(len(optimal_windows[:10])),
            index=default_idx,
            format_func=lambda i: f"{optimal_windows.iloc[i]['Fecha_Lanzamiento']} (MJD {optimal_windows.iloc[i]['Start_MJD']:.3f}) - ΔV: {optimal_windows.iloc[i]['DeltaV']:.2f} km/s",
            key="porkchop_window_selector"
        )
        
        # Guardar el índice seleccionado
        st.session_state['selected_window_idx'] = selected_idx
        
        # Extraer datos de la ventana seleccionada
        selected_mjd = optimal_windows.iloc[selected_idx]['Start_MJD']
        selected_duration = optimal_windows.iloc[selected_idx]['Duration']
        selected_deltav = optimal_windows.iloc[selected_idx]['DeltaV']
        selected_date = optimal_windows.iloc[selected_idx]['Fecha_Lanzamiento']
        
        # Mostrar preview de la ventana seleccionada
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fecha Lanzamiento", selected_date)
            st.caption(f"MJD: {selected_mjd:.3f}")
        with col2:
            st.metric("Duración (días)", f"{selected_duration:.1f}")
        with col3:
            st.metric("ΔV (km/s)", f"{selected_deltav:.2f}")
        
        if st.button("📤 Enviar a Misión Interplanetaria", key="send_to_gmat"):
            logger.info("\n\n" + "="*80)
            logger.info(f"USUARIO: ENVIAR A MISIÓN INTERPLANETARIA - {selected_date} (MJD {selected_mjd:.3f}) | Duración {selected_duration:.1f} días | ΔV {selected_deltav:.2f} km/s")
            logger.info("="*80 + "\n\n")
            
            # Guardar en session_state para la pestaña de Misión Interplanetaria
            st.session_state['ity_epoch_mjd'] = selected_mjd
            st.session_state['ity_flight_duration'] = selected_duration
            st.session_state['ity_epoch_readable'] = selected_date
            st.session_state['ity_data_from_porkchop'] = True
            
            st.success(f"✅ Fecha {selected_date} (MJD {selected_mjd:.3f}) enviada a la Misión Interplanetaria")
            st.info("👉 Ve a la pestaña 'Misión Marte-Tierra' para ejecutar la simulación")
            
            # Forzar actualización de la interfaz
            st.rerun()
    elif 'optimal_windows' in st.session_state:
        st.warning("⚠️ No se encontraron ventanas óptimas con los criterios seleccionados")


# ============================================================================
# TAB 2: GMAT REFINEMENT
# ============================================================================

def render_gmat_tab(gmat_backend):
    """
    Renderiza la pestaña de refinamiento y simulación con GMAT.
    
    Args:
        gmat_backend: Instancia de GmatMission inicializada
    """
    st.header("🛰️ Refinamiento de Órbita con GMAT")
    
    st.markdown("""
    Esta sección permite refinar la trayectoria utilizando GMAT R2025a.
    Puedes usar una fecha del diagrama Porkchop o introducir una manualmente.
    """)
    
    # ========================================================================
    # Estado de carga del script
    # ========================================================================
    if not gmat_backend.is_loaded:
        st.warning("⚠️ El script de GMAT no está cargado")
        
        if st.button("📂 Cargar Script GMAT"):
            with st.spinner("📂 Inicializando GMAT y cargando script de misión... Verificando sintaxis y objetos..."):
                try:
                    success = gmat_backend.load_script()
                    if success:
                        st.success("✅ Script cargado exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al cargar el script. Revisa GMAT_Backend_Log.txt")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        return  # No continuar si el script no está cargado
    
    # ========================================================================
    # Script cargado - Mostrar controles
    # ========================================================================
    st.success("✅ Script GMAT cargado")
    
    # Verificar si hay datos desde Porkchop
    has_porkchop_data = (
        'gmat_epoch_mjd' in st.session_state and 
        st.session_state['gmat_epoch_mjd'] is not None
    )
    
    if has_porkchop_data:
        st.info(f"📥 Fecha recibida desde Porkchop: MJD {st.session_state['gmat_epoch_mjd']:.3f}")
    
    st.divider()
    st.subheader("⚙️ Parámetros de la Misión")
    
    # ========================================================================
    # Inputs de parámetros
    # ========================================================================
    col1, col2 = st.columns(2)
    
    with col1:
        # Época de lanzamiento (MJD)
        default_epoch = st.session_state.get('gmat_epoch_mjd') or 31136.99962962963
        
        epoch_mjd = st.number_input(
            "Época de Lanzamiento (MJD)",
            min_value=30000.0,
            max_value=35000.0,
            value=float(default_epoch),
            step=1.0,
            format="%.6f",
            help="Modified Julian Date de la fecha de lanzamiento"
        )
    
    with col2:
        # Tiempo de vuelo
        default_flight_time = st.session_state.get('gmat_flight_time') or 210.0
        
        flight_time = st.number_input(
            "Tiempo de Vuelo (días)",
            min_value=50.0,
            max_value=500.0,
            value=float(default_flight_time),
            step=1.0,
            help="Duración del viaje en días"
        )
    
    # Convertir MJD a fecha legible
    try:
        # Referencia: MJD 31136.999630 = 2026-04-06
        base_mjd = 31136.999630
        base_date = datetime(2026, 4, 6)
        delta_days = epoch_mjd - base_mjd
        readable_date = base_date + timedelta(days=delta_days)
        
        st.info(f"📅 Fecha aproximada: {readable_date.strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        pass
    
    # ========================================================================
    # Ejecutar simulación
    # ========================================================================
    st.divider()
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        run_simulation = st.button("🚀 Ejecutar Simulación GMAT", type="primary", key="run_gmat_simulation")
    with col_btn2:
        if st.session_state.get('gmat_simulation_success'):
            if st.button("🗑️ Limpiar", key="clear_gmat_results"):
                st.session_state['gmat_simulation_success'] = False
                st.session_state['gmat_results'] = None
                st.rerun()
    
    if run_simulation:
        with st.status("🔬 Ejecutando física de la misión con GMAT R2025a...", expanded=True) as status:
            st.write("⏳ Iniciando motor de física orbital...")
            st.write("📊 GMAT está calculando trayectorias interplanetarias y optimizando órbitas")
            st.write("🚀 Este proceso puede tomar entre 10-30 segundos")
            st.write("")
            st.write("*La pantalla permanecerá atenuada mientras GMAT resuelve las ecuaciones de movimiento orbital...*")
            
            try:
                # Actualizar parámetros
                st.write("🔧 Configurando parámetros de misión...")
                gmat_backend.update_epoch(epoch_mjd)
                gmat_backend.update_flight_time(flight_time)
                
                # Ejecutar misión
                st.write("🎯 Ejecutando simulación completa...")
                success = gmat_backend.run_mission()
                
                if success:
                    st.write("✅ Simulación completada, leyendo resultados...")
                    # Intentar leer resultados
                    results = gmat_backend.get_deltav_results()
                    
                    # Guardar en session_state para mantener resultados
                    st.session_state['gmat_simulation_success'] = True
                    st.session_state['gmat_results'] = results
                    st.session_state['gmat_script_dir'] = os.path.dirname(gmat_backend.script_path)
                    st.session_state['gmat_current_dir'] = os.getcwd()
                    st.session_state['gmat_script_path'] = gmat_backend.script_path
                    
                    status.update(label="✅ Simulación completada exitosamente", state="complete", expanded=False)
                else:
                    st.session_state['gmat_simulation_success'] = False
                    st.session_state['gmat_results'] = None
                    status.update(label="⚠️ La simulación de GMAT falló", state="error", expanded=True)
                    
            except Exception as e:
                st.error(f"❌ Error durante la ejecución: {str(e)}")
                logger.error(f"Error en GMAT execution: {e}", exc_info=True)
                st.session_state['gmat_simulation_success'] = False
                status.update(label="❌ Error en la simulación", state="error", expanded=True)
    
    # Mostrar resultados si existen en session_state
    if st.session_state.get('gmat_simulation_success', False):
        st.success("✅ Simulación completada exitosamente")
        
        # Mostrar información de debug sobre ubicaciones
        with st.expander("🔍 Debug: Ubicaciones de archivos"):
            script_dir = st.session_state.get('gmat_script_dir', '')
            current_dir = st.session_state.get('gmat_current_dir', '')
            script_path = st.session_state.get('gmat_script_path', '')
            
            st.code(f"Directorio del script: {script_dir}")
            st.code(f"Directorio actual: {current_dir}")
            st.code(f"Ruta del script: {script_path}")
            
            # Listar archivos .txt en el directorio del script
            try:
                if script_dir and os.path.exists(script_dir):
                    txt_files = [f for f in os.listdir(script_dir) if f.endswith('.txt')]
                    st.write("Archivos .txt en directorio del script:", txt_files)
            except Exception as e:
                st.write(f"Error al listar archivos: {e}")
        
        results = st.session_state.get('gmat_results')
        
        if results:
                        st.subheader("📊 Resultados de la Simulación")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.markdown("**🚀 Estado Inicial**")
                            st.write(f"Fecha: `{results['initial']['date']}`")
                            st.write(f"Vx: `{results['initial']['velocity']['Vx']:.4f}` km/s")
                            st.write(f"Vy: `{results['initial']['velocity']['Vy']:.4f}` km/s")
                            st.write(f"Vz: `{results['initial']['velocity']['Vz']:.4f}` km/s")
                            
                            v_initial = np.sqrt(
                                results['initial']['velocity']['Vx']**2 +
                                results['initial']['velocity']['Vy']**2 +
                                results['initial']['velocity']['Vz']**2
                            )
                            st.metric("Magnitud V inicial", f"{v_initial:.4f} km/s")
                        
                        with col_b:
                            st.markdown("**🎯 Estado Final**")
                            st.write(f"Fecha: `{results['final']['date']}`")
                            st.write(f"Vx: `{results['final']['velocity']['Vx']:.4f}` km/s")
                            st.write(f"Vy: `{results['final']['velocity']['Vy']:.4f}` km/s")
                            st.write(f"Vz: `{results['final']['velocity']['Vz']:.4f}` km/s")
                            
                            v_final = np.sqrt(
                                results['final']['velocity']['Vx']**2 +
                                results['final']['velocity']['Vy']**2 +
                                results['final']['velocity']['Vz']**2
                            )
                            st.metric("Magnitud V final", f"{v_final:.4f} km/s")
                        
                        # Delta-V total (magnitudes de cambios de velocidad)
                        st.divider()
                        st.warning("""
                        ⚠️ **Nota sobre ΔV**: Los valores mostrados son las magnitudes de velocidad del spacecraft 
                        en el sistema de referencia heliocéntrico. El ΔV real requiere restar las velocidades 
                        orbitales de la Tierra y Marte para obtener las velocidades hiperbólicas (V∞).
                        
                        Para un cálculo aproximado, estos valores dan una estimación del orden de magnitud.
                        """)
                        st.metric(
                            "Magnitud V en lanzamiento",
                            f"{v_initial:.4f} km/s",
                            help="Velocidad heliocéntrica del spacecraft al salir de la Tierra"
                        )
                        st.metric(
                            "Magnitud V en llegada",
                            f"{v_final:.4f} km/s",
                            help="Velocidad heliocéntrica del spacecraft al llegar a Marte"
                        )
        
        else:
            st.warning("⚠️ No se pudieron leer los resultados (archivo DeltaV.txt)")
            st.info("""
            **Posibles causas:**
            - El script GMAT no está configurado para generar el archivo DeltaV.txt
            - El archivo se generó en una ubicación diferente
            - El formato del archivo no es el esperado
            
            **Revisa los logs en la terminal** para ver dónde se buscó el archivo.
            Usa el expander "Debug: Ubicaciones de archivos" arriba para ver las rutas.
            """)
    elif st.session_state.get('gmat_simulation_success') == False:
        st.error("❌ La simulación de GMAT falló. Revisa los logs.")
    
    # ========================================================================
    # Opciones avanzadas
    # ========================================================================
    with st.expander("🔧 Opciones Avanzadas"):
        st.markdown("**Debug: Objetos GMAT en Memoria**")
        if st.button("Ver Objetos GMAT"):
            gmat_backend.show_objects()
            st.info("Revisa la consola/terminal para ver la lista de objetos")


# ============================================================================
# TAB INTERPLANETARY: MISIÓN COMPLETA MARTE-TIERRA
# ============================================================================

def render_interplanetary_mission_tab(script_helio_path: str, script_transfer_path: str):
    """
    Renderiza la pestaña de misión interplanetaria completa Marte-Tierra.
    
    Esta pestaña permite configurar y ejecutar la misión completa de dos fases:
    1. Trayectoria heliocéntrica (GMAT_ITY_Heliocentric.script)
    2. Transferencia completa (GMAT_ITY_transfer.script)
    
    Args:
        script_helio_path: Ruta al script heliocéntrico
        script_transfer_path: Ruta al script de transferencia
    """
    st.header("🚀 Misión Marte-Tierra")
    
    # Indicador de datos recibidos del Porkchop
    if st.session_state.get('ity_data_from_porkchop', False):
        st.info(
            f"📥 **Datos recibidos del Porkchop:** "
            f"Fecha {st.session_state.get('ity_epoch_readable', 'N/A')} "
            f"(MJD {st.session_state.get('ity_epoch_mjd', 0):.3f}), "
            f"Duración {st.session_state.get('ity_flight_duration', 0):.1f} días"
        )
    
    st.markdown("""
    Esta sección ejecuta una misión completa Marte-Tierra en dos fases:
    
    1. **Fase Heliocéntrica**: Calcula la trayectoria y velocidades hiperbólicas
    2. **Fase de Transferencia**: Optimiza la trayectoria completa con B-Plane targets
    
    ---
    """)
    
    # ========================================================================
    # Verificar existencia de scripts
    # ========================================================================
    helio_exists = os.path.exists(script_helio_path)
    transfer_exists = os.path.exists(script_transfer_path)
    
    col_check1, col_check2 = st.columns(2)
    
    with col_check1:
        if helio_exists:
            st.success(f"✅ Script heliocéntrico encontrado")
        else:
            st.error(f"❌ Script heliocéntrico NO encontrado")
            st.code(script_helio_path)
    
    with col_check2:
        if transfer_exists:
            st.success(f"✅ Script de transferencia encontrado")
        else:
            st.error(f"❌ Script de transferencia NO encontrado")
            st.code(script_transfer_path)
    
    if not (helio_exists and transfer_exists):
        st.warning("⚠️ No se pueden ejecutar las misiones sin ambos scripts GMAT.")
        st.info("""
        **Asegúrate de que los scripts existen en el directorio correcto:**
        - GMAT_ITY_Heliocentric.script
        - GMAT_ITY_transfer.script
        
        Cópialos desde el directorio padre al directorio streamlit_app si es necesario.
        """)
        return
    
    st.divider()
    
    # ========================================================================
    # Configuración de Misión
    # ========================================================================
    st.subheader("⚙️ Configuración de Misión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🗓️ Parámetros Temporales**")
        
        # Usar valores del porkchop si están disponibles
        default_epoch = "06 Jun 2026 11:59:28.000"
        default_duration = 350.0
        
        if st.session_state.get('ity_data_from_porkchop', False):
            # Convertir MJD a formato GMAT si tenemos datos del porkchop
            from datetime import datetime, timedelta
            mjd = st.session_state.get('ity_epoch_mjd', 31136.999630)
            base_mjd = 31136.999630
            base_date = datetime.strptime('2026-04-06', '%Y-%m-%d')
            target_date = base_date + timedelta(days=float(mjd) - base_mjd)
            default_epoch = target_date.strftime('%d %b %Y 11:59:28.000')
            default_duration = st.session_state.get('ity_flight_duration', 350.0)
        
        mission_epoch = st.text_input(
            "Época de Misión",
            value=default_epoch,
            help="Formato GMAT: DD Mon YYYY HH:MM:SS.SSS"
        )
        
        flight_duration = st.number_input(
            "Duración de Vuelo (días)",
            min_value=50.0,
            max_value=500.0,
            value=float(default_duration),
            step=10.0
        )
    
    with col2:
        st.markdown("**🛰️ Parámetros Orbitales - Salida (Marte)**")
        
        sma_dep = st.number_input(
            "SMA Salida (km)",
            min_value=3000.0,
            max_value=50000.0,
            value=6500.0,
            step=100.0,
            help="Semi-major axis de órbita de parking en Marte"
        )
        
        inc_dep = st.number_input(
            "Inclinación Salida (deg)",
            min_value=0.0,
            max_value=180.0,
            value=50.0,
            step=1.0
        )
        
        ecc_dep = st.number_input(
            "Excentricidad Salida",
            min_value=0.0,
            max_value=0.99,
            value=0.00000000001,
            format="%.11f",
            help="Casi circular por defecto"
        )
    
    st.markdown("**🌍 Parámetros Orbitales - Llegada (Tierra)**")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        sma_arr = st.number_input(
            "SMA Llegada (km)",
            min_value=6500.0,
            max_value=100000.0,
            value=31780.0,
            step=100.0,
            help="Semi-major axis de órbita objetivo en Tierra"
        )
    
    with col4:
        inc_arr = st.number_input(
            "Inclinación Llegada (deg)",
            min_value=0.0,
            max_value=180.0,
            value=80.0,
            step=1.0
        )
    
    with col5:
        ecc_arr = st.number_input(
            "Excentricidad Llegada",
            min_value=0.0,
            max_value=0.99,
            value=0.7936,
            step=0.0001,
            format="%.4f"
        )
    
    st.divider()
    
    # ========================================================================
    # Ejecutar Misión
    # ========================================================================
    st.subheader("🚀 Ejecución de Misión")
    
    col_btn, col_reset, col_clear = st.columns([3, 1.5, 1])
    
    with col_btn:
        run_mission = st.button(
            "🚀 Ejecutar Misión Interplanetaria Completa",
            type="primary",
            key="run_ity_mission"
        )
    
    with col_reset:
        if st.button("🔄 Reset Valores", key="reset_ity_values"):
            # Limpiar los valores del porkchop
            for key in ['ity_data_from_porkchop', 'ity_epoch_mjd', 'ity_flight_duration', 'ity_epoch_readable']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col_clear:
        if st.session_state.get('ity_mission_complete'):
            if st.button("🗑️ Limpiar", key="clear_ity"):
                for key in ['ity_mission_complete', 'ity_results', 'ity_error']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    if run_mission:
        logger.info("\n\n" + "="*80)
        logger.info("USUARIO: EJECUTAR MISIÓN MARTE-TIERRA")
        logger.info("="*80 + "\n")
        
        try:
            # Crear configuración de misión
            config = MissionConfig(
                mission_epoch=mission_epoch,
                flight_duration=flight_duration,
                sma_dep=sma_dep,
                sma_arr=sma_arr,
                inc_dep=inc_dep,
                inc_arr=inc_arr,
                ecc_dep=ecc_dep,
                ecc_arr=ecc_arr
            )
            logger.info(f"→ Configuración: Época {mission_epoch} | Duración {flight_duration} días | SMA {sma_dep}/{sma_arr} km")
            
            # Mostrar configuración
            with st.expander("📋 Configuración de Misión"):
                st.json(config.to_dict())
            
            # Crear instancia de misión
            mission = InterplanetaryMission(
                script_helio_path=script_helio_path,
                script_transfer_path=script_transfer_path,
                mission_config=config
            )
            
            # Crear contenedor para botón de cancelación
            cancel_placeholder = st.empty()
            
            # Ejecutar con status expandido que muestra mensajes
            with st.status("🚀 Ejecutando Misión Interplanetaria Marte-Tierra (3 fases)", expanded=True) as status:
                # Botón de cancelación dentro del status
                with cancel_placeholder.container():
                    if st.button("⛔ Cancelar Ejecución", key="cancel_gmat", type="secondary", use_container_width=True):
                        st.session_state['cancel_gmat_execution'] = True
                        logger.warning("⚠️ Usuario solicitó cancelación de ejecución")
                
                progress_bar = st.progress(0, text="Iniciando misión...")
                
                # Fase 1: Heliocéntrica
                logger.info("\n" + "-"*80)
                logger.info("FASE 1/3: TRAYECTORIA HELIOCÉNTRICA")
                logger.info("-"*80)
                
                st.write("### 🚀 Fase 1/3: Trayectoria Heliocéntrica")
                st.write("🔬 **GMAT está ejecutando la física orbital...**")
                st.write("⏳ Calculando velocidades hiperbólicas de salida y llegada...")
                st.write("📊 Este proceso resuelve las ecuaciones de movimiento en el sistema solar")
                progress_bar.progress(10, text="Ejecutando fase heliocéntrica...")
                
                # Verificar cancelación antes de fase 1
                if st.session_state.get('cancel_gmat_execution', False):
                    status.update(label="⛔ Ejecución cancelada por el usuario", state="error", expanded=False)
                    st.warning("⚠️ Ejecución cancelada en Fase 1")
                    cancel_placeholder.empty()
                    return
                
                v_dep, v_arr = mission.run_heliocentric_mission()
                logger.info(f"✓ Velocidades calculadas - V∞_dep: {v_dep} | V∞_arr: {v_arr}")
                st.write(f"✅ Velocidades calculadas: V∞_dep = {v_dep}, V∞_arr = {v_arr}")
                progress_bar.progress(40, text="Fase 1 completada")
                
                # Verificar cancelación antes de fase 2
                if st.session_state.get('cancel_gmat_execution', False):
                    status.update(label="⛔ Ejecución cancelada por el usuario", state="error", expanded=False)
                    st.warning("⚠️ Ejecución cancelada después de Fase 1")
                    cancel_placeholder.empty()
                    return
                
                # Fase 2: Cálculo de parámetros
                logger.info("\n" + "-"*80)
                logger.info("FASE 2/3: CÁLCULO DE PARÁMETROS DE REDSON")
                logger.info("-"*80)
                
                st.write("### 🧮 Fase 2/3: Parámetros de Redson (B-Plane)")
                st.write("📐 Procesando vectores de velocidad...")
                st.write("🎯 Calculando parámetros orbitales para targeting B-Plane")
                progress_bar.progress(50, text="Calculando parámetros de Redson...")
                
                params = mission.calculate_transfer_parameters()
                logger.info(f"✓ C3: {params['C3']:.4f} km²/s² | BdotT: {params['BdotT']:.2f} km | BdotR: {params['BdotR']:.2f} km")
                st.write(f"✅ C3 = {params['C3']:.4f} km²/s², BdotT = {params['BdotT']:.2f} km, BdotR = {params['BdotR']:.2f} km")
                progress_bar.progress(60, text="Fase 2 completada")
                
                # Verificar cancelación antes de fase 3
                if st.session_state.get('cancel_gmat_execution', False):
                    status.update(label="⛔ Ejecución cancelada por el usuario", state="error", expanded=False)
                    st.warning("⚠️ Ejecución cancelada después de Fase 2")
                    cancel_placeholder.empty()
                    return
                
                # Fase 3: Transferencia
                logger.info("\n" + "-"*80)
                logger.info("FASE 3/3: TRANSFERENCIA COMPLETA")
                logger.info("-"*80)
                
                st.write("### 🎯 Fase 3/3: Transferencia Completa Marte-Tierra")
                st.write("🔬 **GMAT está ejecutando la simulación física completa...**")
                st.write("⏳ Aplicando parámetros calculados y optimizando trayectoria")
                st.write("🚀 Este es el proceso más largo (~20-30 segundos)")
                st.write("*La pantalla permanecerá atenuada mientras GMAT trabaja...*")
                st.write("💡 **Puedes cancelar la ejecución con el botón de arriba**")
                progress_bar.progress(70, text="Ejecutando transferencia completa...")
                
                final_results = mission.run_transfer_mission()
                
                # Verificar cancelación después de fase 3
                if st.session_state.get('cancel_gmat_execution', False):
                    status.update(label="⛔ Ejecución cancelada por el usuario", state="error", expanded=False)
                    st.warning("⚠️ Ejecución cancelada durante Fase 3")
                    cancel_placeholder.empty()
                    return
                
                progress_bar.progress(100, text="✅ Misión completada")
                
                logger.info("\n" + "="*80)
                logger.info("✅ MISIÓN COMPLETADA EXITOSAMENTE")
                logger.info("="*80 + "\n\n")
                
                # Guardar resultados en session_state
                st.session_state['ity_mission_complete'] = True
                st.session_state['ity_results'] = {
                    'v_departure': v_dep,
                    'v_arrival': v_arr,
                    'redson_params': params,
                    'final_results': final_results
                }
                
                status.update(label="✅ Misión Interplanetaria completada exitosamente", state="complete", expanded=False)
            
            # Limpiar botón de cancelación
            cancel_placeholder.empty()
            st.success("🎉 ¡Misión Interplanetaria completada exitosamente!")
            
        except Exception as e:
            # Verificar si fue una cancelación del usuario
            if st.session_state.get('cancel_gmat_execution', False):
                logger.warning("⚠️ Ejecución cancelada por el usuario durante procesamiento")
                st.warning("⛔ Ejecución cancelada por el usuario")
                if 'cancel_placeholder' in locals():
                    cancel_placeholder.empty()
            else:
                logger.error("\n" + "="*80)
                logger.error(f"❌ ERROR EN MISIÓN: {type(e).__name__} - {str(e)}")
                logger.error("="*80 + "\n\n")
                
                st.error(f"❌ Error durante la ejecución de la misión: {str(e)}")
                logger.error(f"Error en misión interplanetaria: {e}", exc_info=True)
                st.session_state['ity_error'] = str(e)
                
                with st.expander("🐛 Detalles del Error"):
                    import traceback
                    st.code(traceback.format_exc())
    
    # ========================================================================
    # Mostrar Resultados
    # ========================================================================
    if st.session_state.get('ity_mission_complete'):
        st.divider()
        st.subheader("📊 Resultados de la Misión")
        
        results = st.session_state.get('ity_results')
        
        if results:
            # Velocidades Hiperbólicas
            st.markdown("### 🚀 Velocidades Hiperbólicas")
            
            col_v1, col_v2 = st.columns(2)
            
            with col_v1:
                st.markdown("**Salida (Marte)**")
                v_dep = results['v_departure']
                st.write(f"Vx: `{v_dep[0]:.6f}` km/s")
                st.write(f"Vy: `{v_dep[1]:.6f}` km/s")
                st.write(f"Vz: `{v_dep[2]:.6f}` km/s")
                v_dep_mag = np.linalg.norm(v_dep)
                st.metric("Magnitud V∞ Salida", f"{v_dep_mag:.4f} km/s")
            
            with col_v2:
                st.markdown("**Llegada (Tierra)**")
                v_arr = results['v_arrival']
                st.write(f"Vx: `{v_arr[0]:.6f}` km/s")
                st.write(f"Vy: `{v_arr[1]:.6f}` km/s")
                st.write(f"Vz: `{v_arr[2]:.6f}` km/s")
                v_arr_mag = np.linalg.norm(v_arr)
                st.metric("Magnitud V∞ Llegada", f"{v_arr_mag:.4f} km/s")
            
            st.divider()
            
            # Parámetros de Redson
            st.markdown("### 🎯 Parámetros de Redson (B-Plane Targets)")
            
            params = results['redson_params']
            
            # Mostrar parámetros básicos (calculados en Python)
            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                st.metric("C3", f"{params['C3']:.4f} km²/s²")
                st.metric("RHA", f"{params['RHA']:.2f}°")
            
            with col_p2:
                st.metric("DHA", f"{params['DHA']:.2f}°")
                st.metric("BVAZI", f"{params['BVAZI']:.2f}°")
            
            with col_p3:
                st.metric("BdotT", f"{params['BdotT']:.2f} km")
                st.metric("BdotR", f"{params['BdotR']:.2f} km")
            
            # Mostrar RAAN y AOP si están disponibles (calculados por GMAT)
            if 'RAAN' in params and 'AOP' in params:
                st.markdown("#### 🛰️ Parámetros Orbitales (desde GMAT)")
                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    st.metric("RAAN", f"{params['RAAN']:.2f}°")
                with col_o2:
                    st.metric("AOP", f"{params['AOP']:.2f}°")
            
            # Tabla de parámetros
            with st.expander("📋 Tabla Completa de Parámetros"):
                params_df = pd.DataFrame(
                    list(params.items()),
                    columns=['Parámetro', 'Valor']
                )
                st.dataframe(params_df, width='stretch')
            
            st.divider()
            
            # Resultados Finales
            if results.get('final_results'):
                st.markdown("### 📈 Resultados Finales de GMAT")
                
                final = results['final_results']
                
                st.code(final['header'])
                st.code(final['data'])
                
                st.info("""
                **Interpretación de resultados:**
                
                Estos son los valores finales del spacecraft después de completar
                la transferencia optimizada con B-Plane targets y convergencia del solver.
                """)
            
            # Botón para exportar resultados
            st.divider()
            
            st.markdown("### 📥 Exportar Resultados")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                st.markdown("**📄 Script GMAT Personalizado**")
                st.caption("Descarga el .script con tus valores calculados")
                
                if st.button("🎯 Generar Script .script", use_container_width=True):
                    try:
                        from script_generator import generate_custom_script_from_results
                        from pathlib import Path
                        
                        # Ruta a la plantilla
                        template_path = Path(__file__).parent.parent / "PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script"
                        
                        # Preparar configuración de misión (con todos los parámetros)
                        mission_config_dict = {
                            'mission_epoch': mission_epoch,
                            'flight_duration': flight_duration,
                            'sma_dep': sma_dep,
                            'ecc_dep': ecc_dep,
                            'inc_dep': inc_dep,
                            'sma_arr': sma_arr,
                            'ecc_arr': ecc_arr,
                            'inc_arr': inc_arr
                        }
                        
                        # Generar script
                        script_content = generate_custom_script_from_results(
                            template_path=str(template_path),
                            mission_config=mission_config_dict,
                            redson_params=params
                        )
                        
                        # Guardar en session_state para descarga
                        st.session_state['generated_script'] = script_content
                        st.success("✅ Script generado correctamente!")
                        
                    except Exception as e:
                        st.error(f"❌ Error generando script: {str(e)}")
                        logger.error(f"Error en generación de script: {e}", exc_info=True)
                
                # Botón de descarga (solo aparece si hay script generado)
                if 'generated_script' in st.session_state:
                    st.download_button(
                        label="⬇️ Descargar Script GMAT",
                        data=st.session_state['generated_script'],
                        file_name=f"Mision_ITY_{mission_epoch.replace(' ', '_').replace(':', '-')}.script",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            with col_export2:
                st.markdown("**📊 Datos JSON**")
                st.caption("Exporta todos los resultados a formato JSON")
                
                if st.button("💾 Exportar a JSON", use_container_width=True):
                    import json
                    
                    # Convertir arrays numpy a listas para JSON
                    export_data = {
                        'mission_config': {
                            'epoch': mission_epoch,
                            'flight_duration': flight_duration,
                            'sma_dep': sma_dep,
                            'sma_arr': sma_arr,
                            'inc_dep': inc_dep,
                            'inc_arr': inc_arr,
                            'ecc_dep': ecc_dep,
                            'ecc_arr': ecc_arr
                        },
                        'velocities': {
                            'v_departure': v_dep.tolist(),
                            'v_arrival': v_arr.tolist()
                        },
                        'redson_parameters': params,
                        'final_results': final if 'final' in locals() else None
                    }
                    
                    json_str = json.dumps(export_data, indent=2)
                    st.session_state['exported_json'] = json_str
                    st.success("✅ JSON preparado para descarga!")
                
                # Botón de descarga JSON
                if 'exported_json' in st.session_state:
                    st.download_button(
                        label="⬇️ Descargar JSON",
                        data=st.session_state['exported_json'],
                        file_name="interplanetary_mission_results.json",
                        mime="application/json",
                        use_container_width=True
                    )


# ============================================================================
# TAB 3: ABOUT / HELP
# ============================================================================

def render_about_tab():
    """Renderiza la pestaña de información y ayuda."""
    st.header("ℹ️ Acerca de esta Aplicación")
    
    st.markdown("""
    ### 🚀 GMAT + Porkchop Plot - Interfaz Integrada
    
    Esta aplicación combina:
    
    1. **Análisis Porkchop**: Visualización de ventanas de lanzamiento óptimas
       basadas en ΔV y tiempo de vuelo.
    
    2. **Refinamiento GMAT**: Simulación de alta precisión usando GMAT R2025a
       para refinar trayectorias seleccionadas.
    
    ---
    
    ### 📚 Requisitos Técnicos
    
    - **Python**: 3.12
    - **GMAT**: R2025a instalado en `C:\\Users\\mikde\\GMAT_R2025a`
    - **Librerías**: streamlit, pandas, matplotlib, scipy, numpy
    
    ---
    
    ### 🛠️ Arquitectura Modular
    
    - `ity_mission.py`: Lógica de misión Mars-Earth
    - `gmat_backend_ity.py`: Backend de conexión con GMAT para misión interplanetaria
    - `porkchop_manager.py`: Generación de diagramas Porkchop
    - `gui_components.py`: Componentes de interfaz (este archivo)
    - `main_app.py`: Orquestador principal
    
    ---
    
    ### 📖 Cómo Usar
    
    1. **Pestaña Porkchop**: 
       - Configura los parámetros del diagrama
       - Genera el gráfico
       - Busca ventanas óptimas
       - Selecciona una fecha para GMAT
    
    2. **Pestaña GMAT**:
       - Carga el script (primera vez)
       - Usa la fecha del Porkchop o introduce una manual
       - Ejecuta la simulación
       - Revisa los resultados de ΔV
    
    ---
    
    ### ⚠️ Advertencias
    
    - **Rutas**: GMAT es sensible a tildes y espacios. Usa rutas simples.
    - **Logs**: Revisa `GMAT_Backend_Log.txt` si hay errores.
    - **Datos**: Verifica que `DELTA_V_PORKCHOP.txt` tenga el formato correcto.
    
    ---
    
    ### 👨‍💻 Desarrollado por
    
    Ingeniero Aeroespacial - Mikel De Angelis Quevedo - MVP v1.0
    """)
    
    st.divider()
    
    # Información del sistema
    st.subheader("🖥️ Estado del Sistema")
    
    import sys
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Versión Python", f"{sys.version_info.major}.{sys.version_info.minor}")
        st.metric("Versión Streamlit", st.__version__)
    
    with col2:
        gmat_path = r"C:\\Users\\mikde\\GMAT_R2025a"
        gmat_exists = os.path.exists(gmat_path)
        st.metric("GMAT Instalado", "✅ Sí" if gmat_exists else "❌ No")
