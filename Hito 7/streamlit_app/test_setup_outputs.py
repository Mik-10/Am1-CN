"""
Test del sistema de configuración de Outputs
Ejecuta este script para probar que todo funciona correctamente.

Uso:
    python test_setup_outputs.py
"""

import os
import sys
from pathlib import Path

# Añadir el directorio de la app al path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from setup_outputs import (
    get_outputs_dir,
    is_already_configured,
    check_and_setup_if_needed,
    find_report_file_paths,
    SCRIPT_FILES
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_outputs_dir():
    """Test 1: Verificar que se puede obtener/crear la carpeta Outputs."""
    print("\n" + "="*70)
    print("TEST 1: Carpeta Outputs")
    print("="*70)
    
    try:
        outputs_dir = get_outputs_dir()
        print(f"✅ Carpeta Outputs: {outputs_dir}")
        print(f"✅ Existe: {outputs_dir.exists()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_configuration_status():
    """Test 2: Verificar el estado de configuración."""
    print("\n" + "="*70)
    print("TEST 2: Estado de Configuración")
    print("="*70)
    
    try:
        is_configured = is_already_configured()
        print(f"¿Ya configurado?: {is_configured}")
        
        if is_configured:
            print("✅ El sistema ya está configurado")
            marker_file = Path(__file__).parent / ".outputs_configured"
            print(f"   Archivo de marca: {marker_file}")
        else:
            print("ℹ️  Sistema no configurado (primera instalación)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_script_files_exist():
    """Test 3: Verificar que los archivos .script existen."""
    print("\n" + "="*70)
    print("TEST 3: Archivos .script")
    print("="*70)
    
    parent_dir = Path(__file__).parent.parent
    all_exist = True
    
    for script_name in SCRIPT_FILES:
        script_path = parent_dir / script_name
        exists = script_path.exists()
        
        if exists:
            print(f"✅ {script_name}")
        else:
            print(f"❌ {script_name} - NO ENCONTRADO")
            all_exist = False
    
    return all_exist


def test_find_report_files():
    """Test 4: Verificar que se pueden encontrar los ReportFiles en los scripts."""
    print("\n" + "="*70)
    print("TEST 4: Detección de ReportFiles")
    print("="*70)
    
    parent_dir = Path(__file__).parent.parent
    total_found = 0
    
    for script_name in SCRIPT_FILES:
        script_path = parent_dir / script_name
        
        if not script_path.exists():
            print(f"⏭️  {script_name} - OMITIDO (no existe)")
            continue
        
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            report_paths = find_report_file_paths(content)
            
            print(f"\n📄 {script_name}:")
            print(f"   Encontrados: {len(report_paths)} ReportFile(s)")
            
            for report_name, report_path in report_paths:
                filename = os.path.basename(report_path)
                print(f"   - {report_name}: {filename}")
                total_found += 1
            
        except Exception as e:
            print(f"❌ Error al procesar {script_name}: {e}")
            return False
    
    print(f"\n✅ Total de ReportFiles encontrados: {total_found}")
    return total_found > 0


def test_full_setup():
    """Test 5: Ejecutar la configuración completa."""
    print("\n" + "="*70)
    print("TEST 5: Configuración Completa")
    print("="*70)
    
    print("\n⚠️  ADVERTENCIA: Este test modificará los archivos .script")
    print("Presiona ENTER para continuar o Ctrl+C para cancelar...")
    input()
    
    try:
        success = check_and_setup_if_needed()
        
        if success:
            print("\n✅ Configuración completada exitosamente")
        else:
            print("\n⚠️  Configuración completada con advertencias")
        
        return success
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        return False


def verify_script_paths():
    """Test 6: Verificar que las rutas en los scripts son correctas."""
    print("\n" + "="*70)
    print("TEST 6: Verificación de Rutas Actualizadas")
    print("="*70)
    
    parent_dir = Path(__file__).parent.parent
    outputs_dir = get_outputs_dir()
    all_correct = True
    
    for script_name in SCRIPT_FILES:
        script_path = parent_dir / script_name
        
        if not script_path.exists():
            print(f"⏭️  {script_name} - OMITIDO")
            continue
        
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            report_paths = find_report_file_paths(content)
            
            print(f"\n📄 {script_name}:")
            
            for report_name, report_path in report_paths:
                # Verificar si la ruta apunta a la carpeta Outputs correcta
                report_path_clean = report_path.replace('\\\\', '\\')
                
                if str(outputs_dir) in report_path_clean:
                    print(f"   ✅ {report_name}: Ruta correcta")
                else:
                    print(f"   ❌ {report_name}: Ruta incorrecta")
                    print(f"      Actual: {report_path_clean}")
                    print(f"      Esperada contiene: {outputs_dir}")
                    all_correct = False
            
        except Exception as e:
            print(f"❌ Error al verificar {script_name}: {e}")
            all_correct = False
    
    return all_correct


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("🧪 SUITE DE TESTS - SISTEMA DE CONFIGURACIÓN DE OUTPUTS")
    print("="*70)
    
    results = {
        "Carpeta Outputs": test_outputs_dir(),
        "Estado de Configuración": test_configuration_status(),
        "Archivos .script": test_script_files_exist(),
        "Detección de ReportFiles": test_find_report_files(),
    }
    
    # Preguntar si ejecutar la configuración
    print("\n" + "="*70)
    print("¿Deseas ejecutar la configuración completa?")
    print("Esto modificará los archivos .script (S/N): ", end="")
    
    response = input().strip().upper()
    
    if response == 'S':
        results["Configuración Completa"] = test_full_setup()
        results["Verificación de Rutas"] = verify_script_paths()
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE TESTS")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "="*70)
    print(f"Total: {passed}/{total} tests pasaron")
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelados por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
