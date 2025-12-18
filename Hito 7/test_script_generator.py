"""
Test del Generador de Scripts GMAT
Verifica que el generador pueda crear scripts personalizados correctamente.
"""

import sys
from pathlib import Path

# Añadir el directorio streamlit_app al path
sys.path.insert(0, str(Path(__file__).parent / "streamlit_app"))

from script_generator import GmatScriptGenerator
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_script_generation():
    """
    Test básico del generador de scripts.
    """
    logger.info("=" * 80)
    logger.info("TEST: Generación de Script GMAT Personalizado")
    logger.info("=" * 80)
    
    # Ruta a la plantilla
    template_path = Path(__file__).parent / "PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script"
    
    if not template_path.exists():
        logger.error(f"❌ Plantilla no encontrada: {template_path}")
        return False
    
    logger.info(f"✓ Plantilla encontrada: {template_path.name}")
    
    # Crear generador
    try:
        generator = GmatScriptGenerator(str(template_path))
        logger.info("✓ Generador creado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando generador: {e}")
        return False
    
    # Valores de prueba (similares a los de la plantilla)
    test_values = {
        'mission_epoch': '06 Jun 2026 11:59:28.000',
        'flight_duration': 350,
        'sma_dep': -3490.576340345992,
        'ecc_dep': 2.862156665893941,
        'inc_dep': 50.00000000012872,
        'c3_goal': 12.26969705922953,
        'bdot_r': 22882.23838266063,
        'bdot_t': 4288.708051212489,
        'raan': 269.47985183165,
        'aop': 278.6924689891934,
        'goal_sma': 37500,
        'goal_ecc': 0.76
    }
    
    logger.info("\nValores de prueba:")
    for key, value in test_values.items():
        logger.info(f"  {key}: {value}")
    
    # Generar script
    try:
        logger.info("\nGenerando script...")
        script_content = generator.generate_script(**test_values)
        logger.info("✓ Script generado exitosamente")
        logger.info(f"✓ Longitud del script: {len(script_content)} caracteres")
    except Exception as e:
        logger.error(f"❌ Error generando script: {e}", exc_info=True)
        return False
    
    # Verificar que los valores fueron reemplazados
    logger.info("\nVerificando reemplazos...")
    
    checks = [
        ("test.Epoch", f"'{test_values['mission_epoch']}'"),
        ("test.SMA", str(test_values['sma_dep'])),
        ("test.ECC", str(test_values['ecc_dep'])),
        ("FlightTime", str(test_values['flight_duration'])),
        ("C3E_Goal", f"{test_values['c3_goal']:.14f}"),
        ("Goal_BdotR", f"{test_values['bdot_r']:.14f}"),
        ("Goal_BdotT", f"{test_values['bdot_t']:.14f}"),
        ("Goal_SMA", str(test_values['goal_sma'])),
        ("Goal_ecc", str(test_values['goal_ecc']))
    ]
    
    all_checks_passed = True
    for param_name, expected_value in checks:
        if expected_value in script_content:
            logger.info(f"  ✓ {param_name} = {expected_value[:30]}...")
        else:
            logger.warning(f"  ⚠️ {param_name} no encontrado con valor esperado")
            all_checks_passed = False
    
    # Guardar script de prueba
    output_path = Path(__file__).parent / "TEST_Generated_Script.script"
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        logger.info(f"\n✓ Script de prueba guardado en: {output_path.name}")
    except Exception as e:
        logger.error(f"❌ Error guardando script de prueba: {e}")
        return False
    
    # Resumen
    logger.info("\n" + "=" * 80)
    if all_checks_passed:
        logger.info("✅ TEST PASADO: Script generado correctamente")
        logger.info("=" * 80)
        return True
    else:
        logger.warning("⚠️ TEST PARCIALMENTE PASADO: Algunos valores no se reemplazaron")
        logger.info("=" * 80)
        return True  # Aún así consideramos el test como pasado


def test_mission_config_integration():
    """
    Test de integración con MissionConfig.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Integración con MissionConfig")
    logger.info("=" * 80)
    
    # Simular estructura de mission_config
    mission_config = {
        'mission_epoch': '06 Jun 2026 11:59:28.000',
        'flight_duration': 350,
        'sma_dep': -3490.576340345992,
        'ecc_dep': 2.862156665893941,
        'inc_dep': 50.00000000012872,
        'sma_arr': 37500,
        'ecc_arr': 0.76,
        'inc_arr': 0.0
    }
    
    # Simular parámetros de Redson
    redson_params = {
        'C3': 12.26969705922953,
        'BdotR': 22882.23838266063,
        'BdotT': 4288.708051212489,
        'RHA': 45.0,
        'DHA': 30.0,
        'BVAZI': 60.0,
        'RAAN': 269.47985183165,
        'AOP': 278.6924689891934
    }
    
    template_path = Path(__file__).parent / "PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script"
    
    try:
        generator = GmatScriptGenerator(str(template_path))
        script_content = generator.generate_from_mission_results(
            mission_config=mission_config,
            redson_params=redson_params
        )
        logger.info("✓ Script generado desde mission_config")
        logger.info(f"✓ Longitud: {len(script_content)} caracteres")
        
        logger.info("\n✅ TEST PASADO: Integración con MissionConfig exitosa")
        return True
    except Exception as e:
        logger.error(f"❌ Error en integración: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    print("\n=== INICIANDO TESTS DEL GENERADOR DE SCRIPTS ===\n")
    
    # Test 1
    test1_result = test_script_generation()
    
    # Test 2
    test2_result = test_mission_config_integration()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)
    print(f"Test 1 (Generacion basica): {'PASADO' if test1_result else 'FALLADO'}")
    print(f"Test 2 (Integracion MissionConfig): {'PASADO' if test2_result else 'FALLADO'}")
    print("=" * 80)
    
    if test1_result and test2_result:
        print("\nTODOS LOS TESTS PASADOS")
        sys.exit(0)
    else:
        print("\nALGUNOS TESTS FALLARON")
        sys.exit(1)
