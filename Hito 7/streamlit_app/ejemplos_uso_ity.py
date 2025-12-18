"""
Ejemplos de Uso Actualizado - ITY Version
Demuestra cómo usar los módulos actualizados para misiones interplanetarias Mars-Earth.

ACTUALIZADO: Ahora usa GMAT_ITY_Heliocentric.script + GMAT_ITY_transfer.script
"""

import os
import sys
import numpy as np

# ============================================================================
# EJEMPLO 1: Misión Interplanetaria Completa
# ============================================================================

def ejemplo_ity_completa():
    """Demuestra cómo ejecutar una misión interplanetaria completa."""
    
    from gmat_backend_ity import InterplanetaryMission, GmatBackendError
    from ity_mission import MissionConfig
    
    print("=== EJEMPLO: Misión Interplanetaria Completa ===\n")
    
    try:
        # 1. Crear configuración de misión
        config = MissionConfig(
            mission_epoch="06 Jun 2026 11:59:28.000",
            flight_duration=350,
            sma_dep=6500,
            sma_arr=31780,
            inc_dep=50,
            inc_arr=80,
            ecc_dep=0.00000000001,
            ecc_arr=0.7936
        )
        
        print("Configuración de misión:")
        print(config.to_dict())
        print()
        
        # 2. Crear instancia de misión
        mission = InterplanetaryMission(
            script_helio_path="../GMAT_ITY_Heliocentric.script",
            script_transfer_path="../GMAT_ITY_transfer.script",
            mission_config=config
        )
        
        # 3. Ejecutar misión completa
        print("\nEjecutando misión completa...")
        results = mission.run_complete_mission()
        
        # 4. Mostrar resultados
        print("\n" + "="*70)
        print("RESULTADOS")
        print("="*70)
        
        print(f"\nEstado: {results['status']}")
        
        print("\nVelocidades Hiperbólicas:")
        print(f"  V_departure: {results['hyperbolic_velocities']['v_departure']}")
        print(f"  V_arrival: {results['hyperbolic_velocities']['v_arrival']}")
        
        print("\nParámetros de Redson:")
        for key, value in results['redson_parameters'].items():
            print(f"  {key}: {value:.4f}")
        
        if results['final_results']:
            print("\nResultados Finales:")
            print(f"  {results['final_results']['header']}")
            print(f"  {results['final_results']['data']}")
        
    except GmatBackendError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# EJEMPLO 2: Misión Interplanetaria Paso a Paso
# ============================================================================

def ejemplo_ity_paso_a_paso():
    """Demuestra cómo ejecutar cada fase de la misión interplanetaria por separado."""
    
    from gmat_backend_ity import InterplanetaryMission, GmatBackendError
    from ity_mission import MissionConfig
    
    print("=== EJEMPLO: Misión Interplanetaria Paso a Paso ===\n")
    
    try:
        # Configuración
        config = MissionConfig(
            mission_epoch="06 Jun 2026 11:59:28.000",
            flight_duration=350,
            sma_dep=6500,
            sma_arr=31780,
            inc_dep=50,
            inc_arr=80
        )
        
        mission = AM1Mission(
            script_helio_path="../GMAT_AM1_Heliocentric.script",
            script_transfer_path="../GMAT_AM1_transfer.script",
            mission_config=config
        )
        
        # Fase 1: Heliocéntrica
        print("FASE 1: Trayectoria Heliocéntrica")
        print("-" * 70)
        v_dep, v_arr = mission.run_heliocentric_mission()
        print(f"✅ V_departure: {v_dep}")
        print(f"✅ V_arrival: {v_arr}\n")
        
        # Fase 2: Parámetros de Redson
        print("FASE 2: Cálculo de Parámetros de Redson")
        print("-" * 70)
        params = mission.calculate_transfer_parameters()
        for key, value in params.items():
            print(f"  {key}: {value:.4f}")
        print()
        
        # Fase 3: Transferencia
        print("FASE 3: Misión de Transferencia")
        print("-" * 70)
        final_results = mission.run_transfer_mission()
        if final_results:
            print(f"✅ {final_results['header']}")
            print(f"   {final_results['data']}")
        
    except GmatBackendError as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EJEMPLO 3: Uso de Funciones ITY Mission
# ============================================================================

def ejemplo_funciones_ity():
    """Demuestra cómo usar las funciones de ity_mission.py de forma independiente."""
    
    from ity_mission import calculate_redson_parameters, MissionConfig
    
    print("=== EJEMPLO: Funciones ITY Mission ===\n")
    
    # Configuración
    config = MissionConfig(
        mission_epoch="06 Jun 2026 11:59:28.000",
        flight_duration=350,
        sma_dep=6500,
        sma_arr=31780,
        inc_dep=50,
        inc_arr=80
    )
    
    print("Configuración de misión:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    
    # Vectores de velocidad hiperbólica (ejemplo)
    # En una misión real, estos vendrían de GMAT
    v_dep_vec = np.array([1.5, 2.3, 0.5])
    v_arr_vec = np.array([-2.1, 1.8, -0.3])
    
    print("\nVectores de velocidad (ejemplo):")
    print(f"  V_dep: {v_dep_vec}")
    print(f"  V_arr: {v_arr_vec}")
    
    # Calcular parámetros de Redson
    print("\nCalculando parámetros de Redson...")
    params = calculate_redson_parameters(
        v_dep_vec,
        v_arr_vec,
        config.peri_arr,
        config.peri_dep,
        config.inc_dep,
        config.inc_arr
    )
    
    print("\nParámetros de Redson:")
    for key, value in params.items():
        print(f"  {key}: {value:.4f}")


# ============================================================================
# EJEMPLO 4: Porkchop Manager (sin cambios)
# ============================================================================

def ejemplo_porkchop_manager():
    """Demuestra cómo usar PorkchopManager (sin cambios respecto a versión anterior)."""
    
    from porkchop_manager import PorkchopManager
    
    print("=== EJEMPLO: Porkchop Manager ===\n")
    
    try:
        # Cargar datos
        data_file = "../DELTA_V_PORKCHOP.txt"
        
        if not os.path.exists(data_file):
            print(f"❌ No se encuentra el archivo: {data_file}")
            return
        
        manager = PorkchopManager(data_file)
        print(f"✅ Datos cargados: {len(manager.data)} puntos")
        
        # Resumen de datos
        summary = manager.get_data_summary()
        print("\nResumen de datos:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Buscar ventanas óptimas
        print("\nBuscando ventanas óptimas (ΔV < 8.0 km/s)...")
        optimal = manager.get_optimal_launch_window(max_deltav=8.0)
        
        if len(optimal) > 0:
            print(f"\n✅ Encontradas {len(optimal)} ventanas óptimas")
            print("\nPrimeras 5 ventanas:")
            print(optimal[['Start_MJD', 'Duration', 'DeltaV']].head())
        else:
            print("⚠️ No se encontraron ventanas óptimas con ese criterio")
        
        # Generar figura
        print("\nGenerando diagrama Porkchop...")
        fig = manager.get_porkchop_figure()
        print("✅ Figura generada (usa fig.show() para mostrarla)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def main():
    """Menú principal de ejemplos."""
    
    print("\n" + "="*70)
    print("EJEMPLOS DE USO - ITY VERSION")
    print("="*70)
    print("\nSelecciona un ejemplo:")
    print("1. Misión Interplanetaria Completa")
    print("2. Misión Interplanetaria Paso a Paso")
    print("3. Funciones ITY Mission")
    print("4. Porkchop Manager")
    print("0. Salir")
    
    try:
        opcion = input("\nOpción: ").strip()
        
        if opcion == "1":
            ejemplo_ity_completa()
        elif opcion == "2":
            ejemplo_ity_paso_a_paso()
        elif opcion == "3":
            ejemplo_funciones_ity()
        elif opcion == "4":
            ejemplo_porkchop_manager()
        elif opcion == "0":
            print("Saliendo...")
        else:
            print("Opción no válida")
    
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
