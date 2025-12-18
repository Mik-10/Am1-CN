"""
GMAT Backend Module - ITY Version
Encapsula la lógica de conexión y ejecución con GMAT R2025a para misiones interplanetarias.

Esta versión maneja dos scripts GMAT:
1. GMAT_ITY_Heliocentric.script - Calcula la trayectoria heliocéntrica
2. GMAT_ITY_transfer.script - Calcula la transferencia completa

Notas Técnicas:
- Python 3.12 + GMAT R2025a
- CRÍTICO: Evitar tildes, espacios y caracteres especiales en rutas
- Las rutas de script deben ser absolutas
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging
import numpy as np

# Importar el módulo de misión ITY
try:
    from ity_mission import (
        calculate_redson_parameters,
        read_hyperbolic_velocities,
        read_final_results,
        MissionConfig,
        MU_MARS
    )
except ImportError:
    # Si falla, intentar importación relativa
    from .ity_mission import (
        calculate_redson_parameters,
        read_hyperbolic_velocities,
        read_final_results,
        MissionConfig,
        MU_MARS
    )

# ============================================================================
# CONFIGURACIÓN - MODIFICAR SEGÚN TU INSTALACIÓN
# ============================================================================
GMAT_INSTALL_PATH = r"C:\\Users\\mikde\\GMAT_R2025a"
GMAT_BIN_PATH = os.path.join(GMAT_INSTALL_PATH, "bin")
API_STARTUP_FILE = "api_startup_file.txt"

# ============================================================================
# Configuración de Logging
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GmatBackendError(Exception):
    """Excepción personalizada para errores del backend de GMAT."""
    pass


class InterplanetaryMission:
    """
    Clase que encapsula la lógica de ejecución de misiones interplanetarias Mars-Earth.
    
    Maneja dos scripts GMAT secuencialmente:
    1. Script heliocéntrico: Calcula trayectoria y velocidades hiperbólicas
    2. Script de transferencia: Calcula transferencia completa con B-Plane targets
    
    Attributes:
        gmat: Módulo gmatpy cargado dinámicamente
        script_helio_path: Ruta al script heliocéntrico
        script_transfer_path: Ruta al script de transferencia
        mission_config: Configuración de la misión
        is_helio_loaded: Script heliocéntrico cargado
        is_transfer_loaded: Script de transferencia cargado
    """
    
    def __init__(
        self,
        script_helio_path: str,
        script_transfer_path: str,
        mission_config: MissionConfig
    ):
        """
        Inicializa el backend de GMAT para misiones interplanetarias.
        
        Args:
            script_helio_path: Ruta al script GMAT_ITY_Heliocentric.script
            script_transfer_path: Ruta al script GMAT_ITY_transfer.script
            mission_config: Configuración de la misión (MissionConfig)
            
        Raises:
            GmatBackendError: Si GMAT no se puede inicializar
        """
        self.script_helio_path = os.path.abspath(script_helio_path)
        self.script_transfer_path = os.path.abspath(script_transfer_path)
        self.mission_config = mission_config
        
        self.is_helio_loaded = False
        self.is_transfer_loaded = False
        self.gmat = None
        
        # Resultados intermedios
        self.hyperbolic_vels = None
        self.redson_params = None
        self.final_results = None
        
        # Inicializar GMAT
        self._initialize_gmat()
    
    def _initialize_gmat(self):
        """
        Inicializa el módulo GMAT (gmatpy) y configura el entorno.
        
        Raises:
            GmatBackendError: Si no se encuentra GMAT o falla la inicialización
        """
        startup_file = os.path.join(GMAT_BIN_PATH, API_STARTUP_FILE)
        
        if not os.path.exists(startup_file):
            raise GmatBackendError(
                f"No se encuentra el archivo de inicio de GMAT: {startup_file}\n"
                f"Verifica que GMAT esté instalado en: {GMAT_INSTALL_PATH}"
            )
        
        try:
            # Añadir el path de GMAT al sys.path
            if GMAT_BIN_PATH not in sys.path:
                sys.path.insert(1, GMAT_BIN_PATH)
            
            # Importar gmatpy
            import gmatpy as gmat
            gmat.Setup(startup_file)
            self.gmat = gmat
            
            # Configurar logging de GMAT
            self.gmat.UseLogFile("GMAT_ITY_Log.txt")
            self.gmat.EchoLogFile(False)
            
            logger.info("✅ GMAT inicializado correctamente para misiones interplanetarias")
            
        except Exception as e:
            raise GmatBackendError(f"Error al inicializar GMAT: {str(e)}")
    
    def run_heliocentric_mission(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ejecuta el script heliocéntrico para calcular velocidades hiperbólicas.
        
        Returns:
            Tupla (v_dep_vec, v_arr_vec) con vectores de velocidad en km/s
            
        Raises:
            GmatBackendError: Si falla la ejecución
        """
        if not os.path.exists(self.script_helio_path):
            raise GmatBackendError(
                f"Script heliocéntrico no encontrado: {self.script_helio_path}"
            )
        
        try:
            logger.info("🚀 Cargando script heliocéntrico...")
            self.is_helio_loaded = self.gmat.LoadScript(self.script_helio_path)
            
            if not self.is_helio_loaded:
                raise GmatBackendError("LoadScript retornó False para script heliocéntrico")
            
            # Configurar parámetros de misión
            logger.info("⚙️ Configurando parámetros de misión...")
            sc = self.gmat.GetObject("heliocentric_SC")
            test = self.gmat.GetObject("test")
            flight_time_var = self.gmat.GetObject("FlightTime")
            
            sc.SetField("Epoch", str(self.mission_config.mission_epoch))
            test.SetField("Epoch", str(self.mission_config.mission_epoch))
            flight_time_var.SetField("Value", float(self.mission_config.flight_duration))
            
            logger.info(f"  Epoch: {self.mission_config.mission_epoch}")
            logger.info(f"  Flight Time: {self.mission_config.flight_duration} días")
            
            # Ejecutar misión
            logger.info("🚀 Ejecutando misión heliocéntrica...")
            run_result = self.gmat.RunScript()
            
            if not run_result:
                raise GmatBackendError("RunScript falló para misión heliocéntrica")
            
            logger.info("✅ Misión heliocéntrica completada")
            
            # Leer velocidades hiperbólicas
            logger.info("📖 Leyendo velocidades hiperbólicas...")
            v_dep_vec, v_arr_vec = read_hyperbolic_velocities("Heliocentric_hyperbolic_vels.txt")
            
            self.hyperbolic_vels = (v_dep_vec, v_arr_vec)
            
            logger.info(f"  V_departure: {v_dep_vec}")
            logger.info(f"  V_arrival: {v_arr_vec}")
            
            return v_dep_vec, v_arr_vec
            
        except Exception as e:
            raise GmatBackendError(f"Error en misión heliocéntrica: {str(e)}")
    
    def calculate_transfer_parameters(self) -> Dict[str, float]:
        """
        Calcula los parámetros de transferencia (B-Plane targets) usando Redson.
        
        Requiere que run_heliocentric_mission() se haya ejecutado primero.
        
        Returns:
            Dict con parámetros de Redson (C3, RHA, DHA, BVAZI, BdotT, BdotR, RAAN, AOP)
            
        Raises:
            GmatBackendError: Si no se han calculado las velocidades hiperbólicas
        """
        if self.hyperbolic_vels is None:
            raise GmatBackendError(
                "Debes ejecutar run_heliocentric_mission() primero"
            )
        
        try:
            logger.info("🧮 Calculando parámetros de Redson...")
            
            v_dep_vec, v_arr_vec = self.hyperbolic_vels
            
            params = calculate_redson_parameters(
                v_dep_vec,
                v_arr_vec,
                self.mission_config.peri_arr,
                self.mission_config.peri_dep,
                self.mission_config.inc_dep,
                self.mission_config.inc_arr
            )
            
            self.redson_params = params
            
            logger.info("✅ Parámetros de Redson calculados:")
            for key, value in params.items():
                logger.info(f"  {key}: {value:.4f}")
            
            return params
            
        except Exception as e:
            raise GmatBackendError(f"Error al calcular parámetros de Redson: {str(e)}")
    
    def run_transfer_mission(self) -> Dict[str, any]:
        """
        Ejecuta el script de transferencia completa con B-Plane targets.
        
        Requiere que calculate_transfer_parameters() se haya ejecutado primero.
        
        Returns:
            Dict con resultados finales de la misión
            
        Raises:
            GmatBackendError: Si falla la ejecución
        """
        if self.redson_params is None:
            raise GmatBackendError(
                "Debes ejecutar calculate_transfer_parameters() primero"
            )
        
        if not os.path.exists(self.script_transfer_path):
            raise GmatBackendError(
                f"Script de transferencia no encontrado: {self.script_transfer_path}"
            )
        
        try:
            logger.info("🚀 Cargando script de transferencia...")
            self.is_transfer_loaded = self.gmat.LoadScript(self.script_transfer_path)
            
            if not self.is_transfer_loaded:
                raise GmatBackendError("LoadScript retornó False para script de transferencia")
            
            # ================================================================
            # Configurar objeto 'test' para conversión
            # ================================================================
            logger.info("⚙️ Configurando objeto 'test'...")
            test = self.gmat.GetObject("test")
            test.SetField("StateType", "OutgoingAsymptote")
            test.SetField("OutgoingRadPer", self.mission_config.peri_dep)
            test.SetField("OutgoingC3Energy", self.redson_params["C3"])
            test.SetField("OutgoingRHA", self.redson_params["RHA"])
            test.SetField("OutgoingDHA", self.redson_params["DHA"])
            test.SetField("OutgoingBVAZI", self.redson_params["BVAZI"])
            test.SetField("TA", 0)
            
            # Extraer RAAN y AOP del objeto test
            rs_RAAN = test.GetNumber('RAAN')
            rs_AOP = test.GetNumber('AOP')
            
            logger.info(f"  RAAN: {rs_RAAN}")
            logger.info(f"  AOP: {rs_AOP}")
            
            # Guardar RAAN y AOP en los parámetros de Redson
            self.redson_params['RAAN'] = rs_RAAN
            self.redson_params['AOP'] = rs_AOP
            
            # ================================================================
            # Configurar spacecraft 'Sonda_Red_son'
            # ================================================================
            logger.info("⚙️ Configurando spacecraft Red Son...")
            red_son = self.gmat.GetObject("Sonda_Red_son")
            red_son.SetField("Epoch", str(self.mission_config.mission_epoch))
            red_son.SetField("StateType", "Cartesian")
            
            # Calcular estado cartesiano en periapsis
            rp = self.mission_config.sma_dep * (1 - self.mission_config.ecc_dep)
            vp = np.sqrt(
                (MU_MARS / self.mission_config.sma_dep) *
                ((1 + self.mission_config.ecc_dep) / (1 - self.mission_config.ecc_dep))
            )
            
            red_son.SetField("X", rp)
            red_son.SetField("Y", 0)
            red_son.SetField("Z", 0)
            red_son.SetField("VX", 0)
            red_son.SetField("VY", vp)
            red_son.SetField("VZ", 0)
            
            # Cambiar a Keplerian
            red_son.SetField("StateType", "Keplerian")
            red_son.SetField("INC", self.mission_config.inc_dep)
            red_son.SetField("RAAN", rs_RAAN)
            red_son.SetField("AOP", rs_AOP)
            red_son.SetField("TA", 0)
            
            # ================================================================
            # Configurar variables y goals
            # ================================================================
            logger.info("⚙️ Configurando variables y goals...")
            
            # FlightTime
            flight_time_var = self.gmat.GetObject("FlightTime")
            flight_time_var.SetField("Value", float(self.mission_config.flight_duration))
            
            # C3E Goal
            C3E_Goal = self.gmat.GetObject("C3E_Goal")
            C3E_Goal.SetField("Value", float(self.redson_params["C3"]))
            
            # Half Flight Time
            Half_FT = self.gmat.GetObject("Half_Flight_Time")
            Half_FT.SetField("Value", float(self.mission_config.flight_duration / 2))
            
            # B-Plane Goals
            Goal_BdotR = self.gmat.GetObject("Goal_BdotR")
            Goal_BdotR.SetField("Value", float(self.redson_params["BdotR"]))
            
            Goal_BdotT = self.gmat.GetObject("Goal_BdotT")
            Goal_BdotT.SetField("Value", float(self.redson_params["BdotT"]))
            
            # Arrival Orbit Goals
            Goal_SMA = self.gmat.GetObject("Goal_SMA")
            Goal_SMA.SetField("Value", float(self.mission_config.sma_arr))
            
            Goal_ecc = self.gmat.GetObject("Goal_ecc")
            Goal_ecc.SetField("Value", float(self.mission_config.ecc_arr))
            
            # ================================================================
            # Ejecutar misión
            # ================================================================
            logger.info("🚀 Ejecutando script de transferencia...")
            run_result = self.gmat.RunScript()
            
            if not run_result:
                logger.warning("⚠️ RunScript retornó False (puede ser problema de convergencia)")
            else:
                logger.info("✅ Misión de transferencia completada")
            
            # ================================================================
            # Leer resultados finales
            # ================================================================
            logger.info("📖 Leyendo resultados finales...")
            results = read_final_results("Transfer_final_results.txt")
            
            self.final_results = results
            
            if results:
                logger.info(f"  {results['header']}")
                logger.info(f"  {results['data']}")
            
            return results
            
        except Exception as e:
            raise GmatBackendError(f"Error en misión de transferencia: {str(e)}")
    
    def run_complete_mission(self) -> Dict[str, any]:
        """
        Ejecuta la misión completa (heliocéntrica + transferencia).
        
        Returns:
            Dict con todos los resultados de la misión
            
        Raises:
            GmatBackendError: Si falla alguna etapa
        """
        logger.info("=" * 70)
        logger.info("INICIANDO MISIÓN INTERPLANETARIA COMPLETA")
        logger.info("=" * 70)
        
        try:
            # Etapa 1: Misión heliocéntrica
            v_dep, v_arr = self.run_heliocentric_mission()
            
            # Etapa 2: Cálculo de parámetros
            params = self.calculate_transfer_parameters()
            
            # Etapa 3: Misión de transferencia
            final_results = self.run_transfer_mission()
            
            # Compilar resultados
            complete_results = {
                "status": "success",
                "hyperbolic_velocities": {
                    "v_departure": v_dep.tolist(),
                    "v_arrival": v_arr.tolist()
                },
                "redson_parameters": params,
                "final_results": final_results,
                "mission_config": self.mission_config.to_dict()
            }
            
            logger.info("=" * 70)
            logger.info("✅ MISIÓN INTERPLANETARIA COMPLETADA EXITOSAMENTE")
            logger.info("=" * 70)
            
            return complete_results
            
        except Exception as e:
            logger.error("=" * 70)
            logger.error(f"❌ ERROR EN MISIÓN INTERPLANETARIA: {str(e)}")
            logger.error("=" * 70)
            raise GmatBackendError(f"Error en misión completa: {str(e)}")


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    try:
        # Configuración de misión
        config = MissionConfig(
            mission_epoch="06 Jun 2026 11:59:28.000",
            flight_duration=350,
            sma_dep=6500,
            sma_arr=31780,
            inc_dep=50,
            inc_arr=80
        )
        
        # Crear instancia de misión
        mission = InterplanetaryMission(
            script_helio_path="GMAT_ITY_Heliocentric.script",
            script_transfer_path="GMAT_ITY_transfer.script",
            mission_config=config
        )
        
        # Ejecutar misión completa
        results = mission.run_complete_mission()
        
        print("\n" + "=" * 70)
        print("RESULTADOS DE LA MISIÓN")
        print("=" * 70)
        print(f"Estado: {results['status']}")
        print(f"\nVelocidades Hiperbólicas:")
        print(f"  V_dep: {results['hyperbolic_velocities']['v_departure']}")
        print(f"  V_arr: {results['hyperbolic_velocities']['v_arrival']}")
        print(f"\nParámetros de Redson:")
        for key, value in results['redson_parameters'].items():
            print(f"  {key}: {value:.4f}")
        
    except GmatBackendError as e:
        logger.error(f"Error en la misión: {e}")
