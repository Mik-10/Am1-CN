# 🚀 FUNCIONES MÁS INTERESANTES DEL PROYECTO
## Interfaz GMAT + Porkchop Plot con Streamlit

---

## 📋 ÍNDICE

1. [Arquitectura y Caching](#1-arquitectura-y-caching)
2. [Gestión de Estado con Session State](#2-gestión-de-estado-con-session-state)
3. [Cálculos Astronómicos](#3-cálculos-astronómicos)
4. [Integración con GMAT](#4-integración-con-gmat)
5. [Generación Dinámica de Scripts](#5-generación-dinámica-de-scripts)
6. [Configuración Automática](#6-configuración-automática)
7. [Visualización Interactiva](#7-visualización-interactiva)

---

## 1. ARQUITECTURA Y CACHING

### 🔹 Decorador `@st.cache_resource` - Optimización de Carga

**Archivo:** `main_app.py` (línea 116)

```python
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
            st.warning(f"⚠️ No se encuentra el archivo: {data_file}")
            return None
        
        manager = PorkchopManager(data_file)
        logger.info(f"✅ PorkchopManager cargado desde {data_file}")
        return manager
        
    except Exception as e:
        st.error(f"❌ Error al cargar: {str(e)}")
        return None
```

**¿Por qué es interesante?**
- **Persistencia**: El objeto se carga UNA SOLA VEZ y se mantiene en caché
- **Performance**: Evita recargar datos pesados en cada interacción
- **Recurso compartido**: Mismo objeto accesible desde toda la aplicación

**Uso en el código:**
```python
# En main_app.py (línea 250)
porkchop_manager = load_porkchop_manager(str(PORKCHOP_DATA_FILE_PATH))

# Luego se pasa a los tabs sin recargar
render_porkchop_tab(porkchop_manager)
```

---

## 2. GESTIÓN DE ESTADO CON SESSION STATE

### 🔹 Sistema de Cancelación de Ejecución

**Archivo:** `gui_components.py` (línea 688-730)

```python
# Inicializar flag de cancelación
if 'cancel_gmat_execution' not in st.session_state:
    st.session_state['cancel_gmat_execution'] = False

if st.button("🚀 Ejecutar Misión AM1", key="run_am1_mission"):
    # Resetear flag de cancelación
    st.session_state['cancel_gmat_execution'] = False
    
    # Crear contenedor para botón de cancelación
    cancel_placeholder = st.empty()
    
    with st.status("🚀 Ejecutando Misión AM1 (3 fases)", expanded=True):
        # Botón de cancelación
        with cancel_placeholder.container():
            if st.button("⛔ Cancelar Ejecución", key="cancel_gmat"):
                st.session_state['cancel_gmat_execution'] = True
        
        # ... ejecución de fases ...
        
        # Verificar cancelación entre fases
        if st.session_state.get('cancel_gmat_execution', False):
            st.warning("⚠️ Ejecución cancelada")
            cancel_placeholder.empty()
            return
```

**¿Por qué es interesante?**
- **Control de flujo**: Permite detener procesos largos de forma segura
- **Estado persistente**: `session_state` mantiene variables entre reruns
- **UX mejorada**: Feedback visual inmediato al usuario

**Flujo de datos:**
```
Usuario → Botón Cancel → session_state['cancel_gmat_execution'] = True
                                    ↓
                        Verificación entre fases
                                    ↓
                        Detención controlada + Limpieza UI
```

---

## 3. CÁLCULOS ASTRONÓMICOS

### 🔹 Método de Redson - B-Plane Targeting

**Archivo:** `am1_mission.py` (línea 30-108)

```python
def calculate_redson_parameters(
    v_dep_vec: np.ndarray,
    v_arr_vec: np.ndarray,
    rp_arr: float,
    rp_dep: float,
    inc_dep: float,
    inc_arr: float
) -> Dict[str, float]:
    """
    Calcula parámetros B-Plane targets según método de Redson.
    
    Returns:
        Dict con: C3, RHA, DHA, BVAZI, BdotT, BdotR, RAAN, AOP
    """
    
    # --- Mars Departure ---
    C3E = np.dot(v_dep_vec, v_dep_vec)  # Energía característica
    v_dep_norm = np.linalg.norm(v_dep_vec)
    v_dep_unit = v_dep_vec / v_dep_norm
    ecc = 1 + (rp_dep * C3E) / MU_MARS  # Excentricidad hiperbólica
    
    # Ángulos de asíntota hiperbólica
    delta1_rad = np.arcsin(v_dep_unit[2])  # Declinación
    RHA_rad = np.arctan2(v_dep_unit[1], v_dep_unit[0])  # Ascensión recta
    
    # B-Vector Azimuth
    cos_inc = np.cos(np.radians(inc_dep))
    cos_delta = np.cos(delta1_rad)
    val_clamped = np.clip(cos_inc / cos_delta, -1.0, 1.0)
    BVAZI_deg = 90.0 + np.degrees(np.arccos(val_clamped))
    
    # --- Earth Arrival (B-Plane) ---
    v_arr_norm = np.linalg.norm(v_arr_vec)
    v_arr_unit = v_arr_vec / v_arr_norm
    delta_2_rad = np.arcsin(v_arr_unit[2])
    
    # Theta_B & B-Plane components
    cos_inc_2 = np.cos(np.radians(inc_arr))
    cos_delta_2 = np.cos(delta_2_rad)
    theta_b_rad = np.arccos(np.clip(cos_inc_2 / cos_delta_2, -1.0, 1.0))
    
    # Magnitud del B-Plane (Delta)
    term_sqrt = np.sqrt(v_arr_norm**2 + (2 * MU_EARTH / rp_arr))
    DELTA_mag = (rp_arr / v_arr_norm) * term_sqrt
    
    # Componentes T y R del B-Plane
    T_val = DELTA_mag * np.cos(theta_b_rad)
    R_val = DELTA_mag * np.sin(theta_b_rad)
    
    return {
        "C3": C3E,
        "RHA": RHA_deg,
        "DHA": delta1_deg,
        "BVAZI": BVAZI_deg,
        "BdotT": T_val,
        "BdotR": R_val,
    }
```

**¿Por qué es interesante?**
- **Matemáticas complejas**: Trigonometría esférica + mecánica orbital
- **Robustez numérica**: Uso de `np.clip()` para evitar errores de dominio
- **Vectorización**: Operaciones matriciales eficientes con NumPy
- **Aplicación real**: Parámetros usados por GMAT para convergencia

**Contexto físico:**
```
Vectores V∞ (salida/llegada)
        ↓
Conversión a parámetros orbitales (C3, RHA, DHA)
        ↓
Cálculo B-Plane (BdotT, BdotR)
        ↓
Input para GMAT Differential Corrector
```

---

## 4. INTEGRACIÓN CON GMAT

### 🔹 Clase `AM1Mission` - Ejecución Multi-Fase

**Archivo:** `gmat_backend_am1.py` (línea 60-400)

```python
class AM1Mission:
    """
    Encapsula la lógica de ejecución de misiones AM1 Mars-Earth.
    
    Maneja dos scripts GMAT secuencialmente:
    1. Script heliocéntrico: Calcula trayectoria + velocidades hiperbólicas
    2. Script de transferencia: Calcula transferencia completa con B-Plane
    """
    
    def __init__(
        self,
        script_helio_path: str,
        script_transfer_path: str,
        mission_config: MissionConfig
    ):
        self.script_helio_path = os.path.abspath(script_helio_path)
        self.script_transfer_path = os.path.abspath(script_transfer_path)
        self.mission_config = mission_config
        
        self.is_helio_loaded = False
        self.is_transfer_loaded = False
        self.gmat = None
        
        # Inicializar GMAT
        self._initialize_gmat()
    
    def run_heliocentric_mission(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ejecuta FASE 1: Trayectoria heliocéntrica.
        
        Returns:
            Tuple (v_departure, v_arrival): Vectores de velocidad [km/s]
        """
        logger.info("🚀 Ejecutando misión heliocéntrica...")
        
        # Cargar y ejecutar script heliocéntrico
        if not self.is_helio_loaded:
            self.gmat.LoadScript(self.script_helio_path)
            self.is_helio_loaded = True
        
        # Ejecutar misión
        success = self.gmat.RunScript()
        
        if not success:
            raise GmatBackendError("Falló ejecución heliocéntrica")
        
        # Leer resultados de archivo de salida
        v_dep, v_arr = read_hyperbolic_velocities()
        
        logger.info(f"✓ V∞_dep: {v_dep} km/s")
        logger.info(f"✓ V∞_arr: {v_arr} km/s")
        
        return v_dep, v_arr
    
    def calculate_transfer_parameters(self) -> Dict[str, float]:
        """
        Calcula FASE 2: Parámetros de Redson desde velocidades.
        """
        v_dep, v_arr = read_hyperbolic_velocities()
        
        params = calculate_redson_parameters(
            v_dep_vec=v_dep,
            v_arr_vec=v_arr,
            rp_arr=self.mission_config.rp_arr,
            rp_dep=self.mission_config.rp_dep,
            inc_dep=self.mission_config.inc_dep,
            inc_arr=self.mission_config.inc_arr
        )
        
        return params
    
    def run_transfer_mission(self) -> Dict[str, any]:
        """
        Ejecuta FASE 3: Transferencia completa con B-Plane targeting.
        """
        logger.info("🎯 Ejecutando transferencia completa...")
        
        # Cargar script de transferencia
        if not self.is_transfer_loaded:
            self.gmat.LoadScript(self.script_transfer_path)
            self.is_transfer_loaded = True
        
        # Configurar parámetros calculados
        params = self.calculate_transfer_parameters()
        
        # Actualizar variables en GMAT
        self.gmat.GetObject("C3E_Goal").SetField("Value", params['C3'])
        self.gmat.GetObject("Goal_BdotR").SetField("Value", params['BdotR'])
        self.gmat.GetObject("Goal_BdotT").SetField("Value", params['BdotT'])
        
        # Ejecutar con convergencia
        success = self.gmat.RunScript()
        
        if not success:
            raise GmatBackendError("Falló convergencia de transferencia")
        
        # Leer resultados finales
        final_results = read_final_results()
        
        # Extraer RAAN y AOP del spacecraft optimizado
        test_sc = self.gmat.GetObject("test")
        params['RAAN'] = test_sc.GetField("RAAN")
        params['AOP'] = test_sc.GetField("AOP")
        
        return final_results
```

**¿Por qué es interesante?**
- **Arquitectura modular**: Separación clara de responsabilidades
- **Pipeline de datos**: Salida de fase N → entrada de fase N+1
- **Manejo de errores**: Excepciones personalizadas (`GmatBackendError`)
- **Lectura de archivos**: Comunicación Python ↔ GMAT vía archivos de salida
- **State management**: Control de scripts cargados con flags

**Flujo de ejecución:**
```
1. Inicializar GMAT (cargar API)
        ↓
2. FASE 1: Ejecutar trayectoria heliocéntrica
        ↓
3. Leer velocidades hiperbólicas (archivo)
        ↓
4. FASE 2: Calcular parámetros de Redson (Python)
        ↓
5. FASE 3: Ejecutar transferencia con B-Plane
        ↓
6. Leer resultados finales + extraer RAAN/AOP
```

---

## 5. GENERACIÓN DINÁMICA DE SCRIPTS

### 🔹 Clase `GmatScriptGenerator` - Template + Regex

**Archivo:** `script_generator.py` (línea 15-340)

```python
class GmatScriptGenerator:
    """
    Generador de scripts GMAT personalizados basados en plantilla.
    """
    
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        
        # Leer plantilla
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template_content = f.read()
    
    def generate_script(
        self,
        mission_epoch: str,
        flight_duration: float,
        sma_dep: float,
        ecc_dep: float,
        inc_dep: float,
        c3_goal: float,
        bdot_r: float,
        bdot_t: float,
        raan: float = None,
        aop: float = None,
        goal_sma: float = None,
        goal_ecc: float = None,
        output_filename: str = None
    ) -> str:
        """
        Genera un script GMAT personalizado reemplazando valores.
        """
        content = self.template_content
        
        # Reemplazar épocas en TODOS los spacecrafts
        content = self._replace_spacecraft_parameter(
            content, 'heliocentric_SC', 'Epoch', f"'{mission_epoch}'"
        )
        content = self._replace_spacecraft_parameter(
            content, 'test', 'Epoch', f"'{mission_epoch}'"
        )
        content = self._replace_spacecraft_parameter(
            content, 'Sonda_Red_son', 'Epoch', f"'{mission_epoch}'"
        )
        
        # Reemplazar parámetros orbitales en 'test' (hiperbólica)
        content = self._replace_spacecraft_parameter(
            content, 'test', 'SMA', str(sma_dep)
        )
        content = self._replace_spacecraft_parameter(
            content, 'test', 'ECC', str(ecc_dep)
        )
        content = self._replace_spacecraft_parameter(
            content, 'test', 'INC', str(inc_dep)
        )
        
        # Reemplazar variables de misión
        content = self._replace_variable(
            content, 'FlightTime', str(flight_duration)
        )
        content = self._replace_variable(
            content, 'C3E_Goal', f"{c3_goal:.14f}"
        )
        content = self._replace_variable(
            content, 'Goal_BdotR', f"{bdot_r:.14f}"
        )
        content = self._replace_variable(
            content, 'Goal_BdotT', f"{bdot_t:.14f}"
        )
        
        return content
    
    def _replace_spacecraft_parameter(
        self, content: str, spacecraft_name: str, 
        param_name: str, new_value: str
    ) -> str:
        """
        Reemplaza parámetro de spacecraft con regex multiline.
        
        Ejemplo: test.SMA = -3490.576 → test.SMA = <nuevo_valor>
        """
        pattern = rf"^({spacecraft_name}\.{param_name}\s*=\s*)([^;]+)(;)"
        replacement = rf"\g<1>{new_value}\g<3>"
        
        new_content, num_replacements = re.subn(
            pattern, replacement, content, flags=re.MULTILINE
        )
        
        if num_replacements == 0:
            logger.warning(f"⚠️ No se encontró {spacecraft_name}.{param_name}")
        else:
            logger.info(f"✓ {spacecraft_name}.{param_name} = {new_value}")
        
        return new_content
    
    def _replace_variable(
        self, content: str, var_name: str, new_value: str
    ) -> str:
        """
        Reemplaza variable global (sin prefijo spacecraft).
        
        Ejemplo: FlightTime = 350 → FlightTime = <nuevo_valor>
        """
        pattern = rf"^({var_name}\s*=\s*)([^;]+)(;)"
        replacement = rf"\g<1>{new_value}\g<3>"
        
        new_content, num_replacements = re.subn(
            pattern, replacement, content, flags=re.MULTILINE
        )
        
        if num_replacements == 0:
            logger.warning(f"⚠️ No se encontró {var_name}")
        else:
            logger.info(f"✓ {var_name} = {new_value}")
        
        return new_content
```

**¿Por qué es interesante?**
- **Template system**: Plantilla base + valores dinámicos
- **Regex multiline**: Búsqueda precisa con `^` (inicio de línea)
- **Validación automática**: Cuenta reemplazos y alerta si falla
- **Múltiples spacecrafts**: Actualiza 3 objetos diferentes
- **Precisión numérica**: Formato `.14f` para valores científicos

**Proceso de generación:**
```
1. Leer plantilla (.script base)
        ↓
2. Identificar patrones con regex
        ↓
3. Reemplazar valores (spacecraft params + variables)
        ↓
4. Validar cambios (contador de reemplazos)
        ↓
5. Retornar/Guardar script personalizado
```

**Ejemplo de regex:**
```python
# Patrón para: test.SMA = -3490.576340345992;
pattern = r"^(test\.SMA\s*=\s*)([^;]+)(;)"
         # ↑ Inicio línea
         #  ↑ Captura prefijo "test.SMA = "
         #           ↑ Captura valor antiguo (hasta ;)
         #                   ↑ Captura punto y coma

replacement = r"\g<1>NUEVO_VALOR\g<3>"
            # ↑ Mantiene prefijo
            #      ↑ Inserta nuevo valor
            #                   ↑ Mantiene punto y coma
```

---

## 6. CONFIGURACIÓN AUTOMÁTICA

### 🔹 Sistema de Primera Ejecución

**Archivo:** `setup_outputs.py` (línea 36-260)

```python
def get_outputs_dir() -> Path:
    """
    Obtiene o crea la carpeta Outputs en el directorio padre.
    
    Returns:
        Path: Ruta absoluta a la carpeta Outputs
    """
    project_root = Path(__file__).parent.parent
    outputs_dir = project_root / "Outputs"
    
    # Crear si no existe
    outputs_dir.mkdir(exist_ok=True)
    
    return outputs_dir


def is_already_configured() -> bool:
    """
    Verifica si ya se ejecutó la configuración inicial.
    
    Busca archivo marcador .outputs_configured
    """
    marker_file = get_outputs_dir() / ".outputs_configured"
    return marker_file.exists()


def find_report_file_paths(script_content: str) -> List[Tuple[str, str]]:
    """
    Encuentra todas las rutas de ReportFile en un script GMAT.
    
    Usa regex para detectar:
        GMAT <nombre>.Filename = '<ruta>';
    
    Returns:
        Lista de tuplas (nombre_objeto, ruta_archivo)
    """
    pattern = r"GMAT\s+(\w+)\.Filename\s*=\s*'([^']+)';"
    matches = re.findall(pattern, script_content)
    
    return matches


def update_script_paths(script_path: Path, outputs_dir: Path) -> bool:
    """
    Actualiza TODAS las rutas de ReportFile en un script.
    
    Proceso:
        1. Leer contenido del script
        2. Encontrar rutas de ReportFile (regex)
        3. Para cada ruta:
           - Extraer nombre de archivo
           - Construir nueva ruta: <outputs_dir>/<filename>
           - Reemplazar en contenido
        4. Guardar script modificado
    
    Returns:
        True si se hicieron cambios, False si no
    """
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    report_files = find_report_file_paths(content)
    
    for obj_name, old_path in report_files:
        # Extraer nombre de archivo
        filename = Path(old_path).name
        
        # Construir nueva ruta (absoluta)
        new_path = outputs_dir / filename
        new_path_str = str(new_path).replace('\\', '\\\\')
        
        # Reemplazar en contenido
        old_pattern = rf"GMAT\s+{obj_name}\.Filename\s*=\s*'[^']+';"
        new_line = f"GMAT {obj_name}.Filename = '{new_path_str}';"
        
        content = re.sub(old_pattern, new_line, content)
        
        logger.info(f"✓ {obj_name}: {filename} → {outputs_dir.name}/")
    
    if content != original_content:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def check_and_setup_if_needed() -> bool:
    """
    Verifica y ejecuta configuración automática en primera ejecución.
    
    Flow:
        1. ¿Ya configurado? → Salir
        2. No → Ejecutar setup_outputs()
        3. Marcar como configurado
    
    Llamada desde main_app.py al inicio de la aplicación.
    """
    if is_already_configured():
        logger.info("✓ Outputs ya configurados")
        return True
    
    logger.info("Primera ejecución detectada. Configurando Outputs...")
    
    success = setup_outputs()
    
    if success:
        mark_as_configured()
        logger.info("✅ Configuración completada")
    
    return success
```

**¿Por qué es interesante?**
- **First-run detection**: Archivo marcador `.outputs_configured`
- **Portabilidad**: Rutas absolutas calculadas dinámicamente
- **Regex avanzado**: Extracción de patrones complejos en scripts GMAT
- **Modificación segura**: Lee → Modifica → Escribe (atomic)
- **User-friendly**: Configuración automática sin intervención manual

**Flujo de configuración:**
```
App inicia
    ↓
check_and_setup_if_needed()
    ↓
¿Existe .outputs_configured? → SÍ → Skip
    ↓ NO
Crear carpeta Outputs/
    ↓
Para cada .script:
    - Buscar ReportFile.Filename
    - Reemplazar ruta → Outputs/<filename>
    - Guardar script
    ↓
Crear .outputs_configured
```

---

## 7. VISUALIZACIÓN INTERACTIVA

### 🔹 Diagrama Porkchop con Matplotlib + SciPy

**Archivo:** `porkchop_manager.py` (línea 132-220)

```python
def get_porkchop_figure(
    self, 
    deltav_min: float = 6.0,
    deltav_max: float = 13.0,
    deltav_step: float = 0.5,
    tof_levels: list = None,
    figsize: Tuple[int, int] = (12, 8)
) -> plt.Figure:
    """
    Genera diagrama Porkchop con contornos de ΔV y TOF.
    
    Args:
        deltav_min: DeltaV mínimo para contornos (km/s)
        deltav_max: DeltaV máximo para contornos (km/s)
        deltav_step: Paso entre contornos (km/s)
        tof_levels: Niveles de Time of Flight (días)
        
    Returns:
        Figura de matplotlib lista para mostrar
    """
    if self.datos is None:
        raise ValueError("No hay datos cargados")
    
    if tof_levels is None:
        tof_levels = [290, 310, 330, 350]
    
    # Calcular fecha de llegada en MJD
    self.datos['Fecha_Llegada_MJD'] = (
        self.datos['Start_MJD'] + self.datos['Duration']
    )
    
    # Puntos dispersos (X=Lanzamiento, Y=Llegada, Z=DeltaV)
    x = self.datos['Start_MJD']
    y = self.datos['Fecha_Llegada_MJD']
    z_deltav = self.datos['DeltaV']
    z_tof = self.datos['Duration']
    
    # Crear grilla uniforme para interpolación
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.linspace(y.min(), y.max(), 300)
    Xi, Yi = np.meshgrid(xi, yi)
    
    # Interpolar datos dispersos → grilla (método cubic)
    from scipy.interpolate import griddata
    
    Zi_deltav = griddata(
        points=(x, y),
        values=z_deltav,
        xi=(Xi, Yi),
        method='cubic'
    )
    
    Zi_tof = griddata(
        points=(x, y),
        values=z_tof,
        xi=(Xi, Yi),
        method='cubic'
    )
    
    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=figsize)
    
    # Contornos de DeltaV (líneas gruesas, colores)
    contour_deltav = ax.contour(
        Xi, Yi, Zi_deltav,
        levels=np.arange(deltav_min, deltav_max + deltav_step, deltav_step),
        cmap='coolwarm',
        linewidths=2
    )
    ax.clabel(contour_deltav, inline=True, fontsize=10, fmt='%.1f km/s')
    
    # Contornos de TOF (líneas punteadas, negras)
    contour_tof = ax.contour(
        Xi, Yi, Zi_tof,
        levels=tof_levels,
        colors='black',
        linestyles='dashed',
        linewidths=1.5
    )
    ax.clabel(contour_tof, inline=True, fontsize=9, fmt='%d días')
    
    # Convertir MJD → fechas legibles para etiquetas
    def mjd_to_date(mjd):
        from datetime import datetime, timedelta
        mjd_epoch = datetime(1858, 11, 17)
        return mjd_epoch + timedelta(days=mjd)
    
    # Formatear ejes con fechas
    from matplotlib.dates import DateFormatter
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    
    # Etiquetas y título
    ax.set_xlabel('Fecha de Lanzamiento', fontsize=12)
    ax.set_ylabel('Fecha de Llegada', fontsize=12)
    ax.set_title('Diagrama Porkchop: Marte → Tierra', fontsize=14, weight='bold')
    
    # Colorbar para DeltaV
    cbar = fig.colorbar(contour_deltav, ax=ax, label='ΔV Total (km/s)')
    
    # Grid y ajustes
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    
    return fig


def get_optimal_launch_window(self, max_deltav: float = 8.0) -> pd.DataFrame:
    """
    Encuentra ventanas de lanzamiento óptimas (menor DeltaV).
    
    Args:
        max_deltav: DeltaV máximo aceptable (km/s)
        
    Returns:
        DataFrame con las 10 mejores opciones ordenadas por DeltaV
    """
    if self.datos is None:
        return pd.DataFrame()
    
    # Filtrar por DeltaV máximo
    filtered = self.datos[self.datos['DeltaV'] <= max_deltav].copy()
    
    # Ordenar por DeltaV ascendente
    optimal = filtered.sort_values('DeltaV').head(10)
    
    logger.info(f"Encontradas {len(optimal)} ventanas óptimas")
    
    return optimal
```

**¿Por qué es interesante?**
- **Interpolación 2D**: SciPy `griddata` convierte puntos dispersos → grilla suave
- **Doble contorno**: ΔV (colores) + TOF (líneas punteadas) en mismo plot
- **Conversión de fechas**: MJD → datetime para ejes legibles
- **Optimización**: Búsqueda automática de ventanas con menor costo
- **Customización**: Múltiples parámetros para ajustar visualización

**Pipeline de visualización:**
```
Datos dispersos (x, y, z)
        ↓
Crear grilla uniforme (meshgrid)
        ↓
Interpolar con scipy.griddata (cubic)
        ↓
Generar contornos (ΔV + TOF)
        ↓
Formatear ejes (fechas legibles)
        ↓
Añadir colorbar + grid
        ↓
Retornar figura matplotlib
```

---

## 📊 RESUMEN DE TÉCNICAS CLAVE

| Técnica | Archivo | Utilidad |
|---------|---------|----------|
| `@st.cache_resource` | main_app.py | Caché de objetos pesados |
| Session State | gui_components.py | Estado persistente entre reruns |
| NumPy Vectorización | am1_mission.py | Cálculos astronómicos eficientes |
| Regex Multiline | script_generator.py | Modificación precisa de scripts |
| Interpolación 2D | porkchop_manager.py | Visualización suave de datos dispersos |
| Pipeline Multi-Fase | gmat_backend_am1.py | Ejecución secuencial con state |
| First-Run Detection | setup_outputs.py | Configuración automática portable |

---

## 🎯 CONCEPTOS AVANZADOS APLICADOS

### 1. **Patrón MVC (Model-View-Controller)**
- **Model**: `am1_mission.py`, `porkchop_manager.py` (lógica de negocio)
- **View**: `gui_components.py` (interfaz pura)
- **Controller**: `main_app.py` (orquestación)

### 2. **Separation of Concerns**
- Backend GMAT separado de cálculos Python
- GUI desacoplada de lógica de datos
- Configuración centralizada en `config.py`

### 3. **Error Handling Robusto**
```python
try:
    # Operación riesgosa
    result = gmat.RunScript()
except GmatBackendError as e:
    logger.error(f"Error GMAT: {e}")
    st.error("❌ Fallo en simulación")
except Exception as e:
    logger.error(f"Error inesperado: {e}", exc_info=True)
    st.error("❌ Error crítico")
finally:
    # Limpieza
    cleanup_resources()
```

### 4. **Lazy Loading + Caching**
```python
@st.cache_resource
def load_heavy_resource():
    # Se ejecuta UNA SOLA VEZ
    return expensive_operation()

# Uso posterior: instant retrieval
resource = load_heavy_resource()
```

### 5. **State Machine Pattern**
```python
# Estado de configuración
if not is_configured():
    setup()
    mark_configured()

# Estado de ejecución
if executing:
    if cancel_requested:
        transition_to_cancelled()
    else:
        continue_execution()
```

---

## 💡 CONSEJOS PARA LA PRESENTACIÓN

### Diapositiva 1: Arquitectura General
- Diagrama de flujo: Datos → Processing → Visualización
- Destacar separación de módulos

### Diapositiva 2-3: Caching y Performance
- Comparar tiempos: Con/Sin `@st.cache_resource`
- Mostrar código del decorador

### Diapositiva 4-5: Cálculos Astronómicos
- Ecuaciones matemáticas (LaTeX)
- Código de `calculate_redson_parameters()`
- Diagrama B-Plane

### Diapositiva 6-7: Integración GMAT
- Diagrama de fases (1→2→3)
- Código de `AM1Mission.run_heliocentric_mission()`
- Screenshot de ejecución

### Diapositiva 8-9: Generación Dinámica
- Ejemplo de template + regex
- Before/After de script generado

### Diapositiva 10: Configuración Automática
- Diagrama de first-run detection
- Código de `check_and_setup_if_needed()`

### Diapositiva 11: Visualización
- Mostrar Porkchop plot resultante
- Código de interpolación con `griddata`

### Diapositiva 12: Conclusiones
- Técnicas aplicadas (lista)
- Resultados obtenidos (métricas)
- Lecciones aprendidas

---

## 📚 REFERENCIAS TÉCNICAS

- **Streamlit Documentation**: https://docs.streamlit.io/
- **NumPy User Guide**: https://numpy.org/doc/stable/
- **SciPy Interpolation**: https://docs.scipy.org/doc/scipy/reference/interpolate.html
- **GMAT API**: https://gmat.gsfc.nasa.gov/
- **Matplotlib Gallery**: https://matplotlib.org/stable/gallery/index.html
- **Regex Python**: https://docs.python.org/3/library/re.html

---

**Generado para presentación académica - Asignatura de Programación**
**Proyecto: Interfaz GMAT + Porkchop Plot**
**Fecha: Diciembre 2025**
