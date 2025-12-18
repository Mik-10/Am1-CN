"""
ITY Mission Module (Interplanetary)
Funciones para calcular parámetros de misión Mars-Earth.

Este módulo encapsula la lógica de cálculo de parámetros de Redson (B-Plane)
y configuración de misiones interplanetarias para GMAT.
"""

import numpy as np
import os
import logging
from typing import Dict, Optional, Tuple

# Configuración de logging
logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTES
# ============================================================================

MU_MARS = 42828.44      # km³/s² - Mars gravitational parameter
MU_EARTH = 3.9860e5     # km³/s² - Earth gravitational parameter


# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def calculate_redson_parameters(
    v_dep_vec: np.ndarray,
    v_arr_vec: np.ndarray,
    rp_arr: float,
    rp_dep: float,
    inc_dep: float,
    inc_arr: float
) -> Dict[str, float]:
    """
    Calcula parámetros B-Plane targets y parámetros orbitales desde vectores de velocidad.
    
    Basado en el método de Redson para transferencias interplanetarias.
    
    Args:
        v_dep_vec: Vector de velocidad de salida [Vx, Vy, Vz] en km/s
        v_arr_vec: Vector de velocidad de llegada [Vx, Vy, Vz] en km/s
        rp_arr: Radio de periapsis de llegada (Earth) en km
        rp_dep: Radio de periapsis de salida (Mars) en km
        inc_dep: Inclinación de órbita de salida en grados
        inc_arr: Inclinación de órbita de llegada en grados
        
    Returns:
        Dict con los siguientes parámetros:
            - C3: Energía característica (km²/s²)
            - RHA: Right Ascension of Hyperbolic Asymptote (grados)
            - DHA: Declination of Hyperbolic Asymptote (grados)
            - BVAZI: B-Vector Azimuth (grados)
            - BdotT: Componente T del B-Plane (km)
            - BdotR: Componente R del B-Plane (km)
            - RAAN: Right Ascension of Ascending Node (grados)
            - AOP: Argument of Periapsis (grados)
    """
    
    # --- Mars Departure ---
    C3E = np.dot(v_dep_vec, v_dep_vec)
    v_dep_norm = np.linalg.norm(v_dep_vec)
    v_dep_unit = v_dep_vec / v_dep_norm
    ecc = 1 + (rp_dep * C3E) / MU_MARS
    
    # Ángulos (convertidos a grados para GMAT)
    delta1_rad = np.arcsin(v_dep_unit[2])
    delta1_deg = np.degrees(delta1_rad)
    RHA_rad = np.arctan2(v_dep_unit[1], v_dep_unit[0])
    RHA_deg = np.degrees(RHA_rad)
    
    # BVAZI
    cos_inc = np.cos(np.radians(inc_dep))
    cos_delta = np.cos(delta1_rad)
    val_clamped = np.clip(cos_inc / cos_delta, -1.0, 1.0)
    BVAZI_deg = 90.0 + np.degrees(np.arccos(val_clamped))
    
    # --- Earth Arrival ---
    v_arr_norm = np.linalg.norm(v_arr_vec)
    v_arr_unit = v_arr_vec / v_arr_norm
    delta_2_rad = np.arcsin(v_arr_unit[2])
    
    # Theta_B & B-Plane
    cos_inc_2 = np.cos(np.radians(inc_arr))
    cos_delta_2 = np.cos(delta_2_rad)
    val_clamped_2 = np.clip(cos_inc_2 / cos_delta_2, -1.0, 1.0)
    theta_b_rad = np.arccos(val_clamped_2)
    
    # Calcular magnitud B-Plane (Delta)
    term_sqrt = np.sqrt(v_arr_norm**2 + (2 * MU_EARTH / rp_arr))
    DELTA_mag = (rp_arr / v_arr_norm) * term_sqrt
    
    # Calcular componentes B-dot
    T_val = DELTA_mag * np.cos(theta_b_rad)
    R_val = DELTA_mag * np.sin(theta_b_rad)
    
    # NOTA: Los parámetros RAAN y AOP se obtienen desde GMAT usando el objeto 'test'
    # configurado en OutgoingAsymptote. No se calculan aquí porque GMAT hace
    # la conversión automáticamente desde C3, RHA, DHA, BVAZI.
    # Ver gmat_backend_am1.py::run_transfer_mission() para detalles.
    
    return {
        "C3": C3E,
        "RHA": RHA_deg,
        "DHA": delta1_deg,
        "BVAZI": BVAZI_deg,
        "BdotT": T_val,
        "BdotR": R_val,
    }


def read_hyperbolic_velocities(file_path: str = "Heliocentric_hyperbolic_vels.txt") -> Tuple[np.ndarray, np.ndarray]:
    """
    Lee vectores de velocidad hiperbólica desde el archivo de salida de GMAT.
    
    Args:
        file_path: Nombre del archivo de salida (por defecto "Heliocentric_hyperbolic_vels.txt")
        
    Returns:
        Tupla (initial_velocity_vec, final_velocity_vec) en km/s
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el formato del archivo es incorrecto
    """
    # Los archivos ahora están en la carpeta Outputs del directorio padre
    outputs_dir = os.path.join(os.path.dirname(__file__), "..", "Outputs")
    full_path = os.path.join(outputs_dir, file_path)
    
    if not os.path.exists(full_path):
        logger.error(f"Archivo no encontrado: {full_path}")
        raise FileNotFoundError(f"No se encuentra el archivo: {full_path}")
    
    logger.info(f"Leyendo archivo: {full_path}")
    file_path = full_path
    
    try:
        with open(file_path, "r") as f:
            lines = [line.rstrip() for line in f if line.strip()]
        
        if len(lines) < 4:
            raise ValueError("El archivo tiene menos de 4 líneas válidas")
        
        # Extraer las últimas 4 líneas (formato del script original)
        initial_date = lines[-4]
        final_date = lines[-3]
        
        initial_values = initial_date.split()
        initial_velocity_vec = np.array([
            float(initial_values[4]),
            float(initial_values[5]),
            float(initial_values[6])
        ])
        
        final_values = final_date.split()
        final_velocity_vec = np.array([
            float(final_values[4]),
            float(final_values[5]),
            float(final_values[6])
        ])
        
        logger.info(f"Velocidad inicial: {initial_velocity_vec}")
        logger.info(f"Velocidad final: {final_velocity_vec}")
        
        return initial_velocity_vec, final_velocity_vec
        
    except (IndexError, ValueError) as e:
        raise ValueError(f"Error al parsear el archivo: {str(e)}")


def read_final_results(file_path: str = "Transfer_final_results.txt") -> Optional[Dict[str, any]]:
    """
    Lee los resultados finales de la misión desde el archivo de salida de GMAT.
    
    Args:
        file_path: Nombre del archivo de salida (por defecto "Transfer_final_results.txt")
        
    Returns:
        Dict con los resultados parseados o None si falla
    """
    # Los archivos ahora están en la carpeta Outputs del directorio padre
    outputs_dir = os.path.join(os.path.dirname(__file__), "..", "Outputs")
    full_path = os.path.join(outputs_dir, file_path)
    
    if not os.path.exists(full_path):
        logger.warning(f"Archivo no encontrado: {full_path}")
        return None
    
    logger.info(f"Leyendo archivo: {full_path}")
    file_path = full_path
    
    try:
        with open(file_path, "r") as f:
            lines = [line.rstrip() for line in f if line.strip()]
        
        if len(lines) < 2:
            logger.warning("El archivo tiene menos de 2 líneas")
            return None
        
        final_data_header = lines[-2]
        final_data = lines[-1]
        
        logger.info(f"Header: {final_data_header}")
        logger.info(f"Data: {final_data}")
        
        return {
            "header": final_data_header,
            "data": final_data
        }
        
    except Exception as e:
        logger.error(f"Error al leer resultados finales: {str(e)}")
        return None


# ============================================================================
# CLASE DE CONFIGURACIÓN DE MISIÓN
# ============================================================================

class MissionConfig:
    """
    Clase para almacenar y validar la configuración de una misión Mars-Earth.
    """
    
    def __init__(
        self,
        mission_epoch: str,
        flight_duration: float,
        sma_dep: float,
        sma_arr: float,
        inc_dep: float,
        inc_arr: float,
        ecc_dep: float = 0.00000000001,
        ecc_arr: float = 0.7936
    ):
        """
        Inicializa la configuración de misión.
        
        Args:
            mission_epoch: Fecha de la misión en formato GMAT (ej: "06 Jun 2026 11:59:28.000")
            flight_duration: Duración del vuelo en días
            sma_dep: Semi-major axis de órbita de salida (km)
            sma_arr: Semi-major axis de órbita de llegada (km)
            inc_dep: Inclinación de órbita de salida (grados)
            inc_arr: Inclinación de órbita de llegada (grados)
            ecc_dep: Excentricidad de órbita de salida (default: ~0)
            ecc_arr: Excentricidad de órbita de llegada (default: 0.7936)
        """
        self.mission_epoch = mission_epoch
        self.flight_duration = flight_duration
        self.sma_dep = sma_dep
        self.sma_arr = sma_arr
        self.inc_dep = inc_dep
        self.inc_arr = inc_arr
        self.ecc_dep = ecc_dep
        self.ecc_arr = ecc_arr
        
        # Calcular periapsis
        self.peri_dep = sma_dep * (1 - ecc_dep)
        self.peri_arr = sma_arr * (1 - ecc_arr)
    
    def to_dict(self) -> Dict[str, any]:
        """Retorna la configuración como diccionario."""
        return {
            "mission_epoch": self.mission_epoch,
            "flight_duration": self.flight_duration,
            "sma_dep": self.sma_dep,
            "sma_arr": self.sma_arr,
            "inc_dep": self.inc_dep,
            "inc_arr": self.inc_arr,
            "ecc_dep": self.ecc_dep,
            "ecc_arr": self.ecc_arr,
            "peri_dep": self.peri_dep,
            "peri_arr": self.peri_arr
        }
    
    def __repr__(self):
        return f"MissionConfig(epoch={self.mission_epoch}, duration={self.flight_duration}d)"


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Configuración de ejemplo
    config = MissionConfig(
        mission_epoch="06 Jun 2026 11:59:28.000",
        flight_duration=350,
        sma_dep=6500,
        sma_arr=31780,
        inc_dep=50,
        inc_arr=80
    )
    
    print("Configuración de misión:")
    print(config.to_dict())
    
    # Ejemplo de cálculo de parámetros (requiere vectores de velocidad)
    # Estos normalmente vienen del primer script de GMAT
    v_dep = np.array([1.5, 2.3, 0.5])  # Ejemplo
    v_arr = np.array([-2.1, 1.8, -0.3])  # Ejemplo
    
    params = calculate_redson_parameters(
        v_dep, v_arr,
        config.peri_arr, config.peri_dep,
        config.inc_dep, config.inc_arr
    )
    
    print("\nParámetros de Redson:")
    for key, value in params.items():
        print(f"  {key}: {value:.4f}")
