# ✅ SISTEMA DE CONFIGURACIÓN AUTOMÁTICA DE OUTPUTS - IMPLEMENTADO

## 🎯 Objetivo Cumplido

Se ha implementado un sistema que **SOLO LA PRIMERA VEZ** que se instala el programa:

1. ✅ Obtiene/crea la carpeta `Outputs` en el directorio padre de la app
2. ✅ Edita los 3 archivos `.script` de GMAT actualizando las rutas absolutas
3. ✅ Mantiene los nombres de archivos sin cambios
4. ✅ Guarda la configuración para no repetir el proceso

## 📁 Archivos Creados/Modificados

### Nuevos Archivos

1. **`streamlit_app/setup_outputs.py`** (267 líneas)
   - Módulo principal de configuración
   - Funciones: `check_and_setup_if_needed()`, `setup_outputs()`, `force_reconfigure()`
   - Detecta primera instalación y configura automáticamente

2. **`streamlit_app/OUTPUTS_CONFIG_README.md`**
   - Documentación completa del sistema
   - Casos de uso y solución de problemas
   - Ejemplos de logs

3. **`streamlit_app/test_setup_outputs.py`**
   - Suite de tests para verificar funcionamiento
   - 6 tests: carpeta, estado, scripts, reportfiles, configuración, verificación

4. **`streamlit_app/.outputs_configured`** (se crea automáticamente)
   - Archivo de marca que indica configuración completada
   - Si se elimina, se vuelve a ejecutar la configuración

### Archivos Modificados

5. **`streamlit_app/main_app.py`**
   - ✅ Importa `setup_outputs`
   - ✅ Ejecuta `check_and_setup_if_needed()` al inicio
   - ✅ Añadido botón "🛠️ Reconfigurar Outputs" en sidebar

6. **`streamlit_app/am1_mission.py`** (modificado previamente)
   - ✅ Ya lee desde `../Outputs/` (sin lógica de possible_paths)

## 🔧 Cómo Funciona

### Primera Ejecución (Usuario Nuevo)

```
streamlit run main_app.py
↓
1. Detecta que no existe .outputs_configured
2. Ejecuta setup_outputs()
   ├─ Crea Outputs/ en directorio padre
   ├─ Lee GMAT_AM1_Heliocentric.script
   │  └─ Actualiza 2 rutas (.Filename)
   ├─ Lee GMAT_AM1_transfer.script
   │  └─ Actualiza 2 rutas (.Filename)
   ├─ Lee PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script
   │  └─ Actualiza 2 rutas (.Filename)
   └─ Crea .outputs_configured
3. Aplicación lista ✅
```

### Ejecuciones Posteriores

```
streamlit run main_app.py
↓
1. Detecta que existe .outputs_configured
2. No ejecuta configuración (ya está listo)
3. Aplicación arranca normalmente ✅
```

## 📝 Qué se Modifica en los .script

### ANTES (ruta hardcoded):
```gmat
hyperbolic_vels.Filename = 'C:\Users\mikde\Desktop\ETSIAE\MUSE\11 - PRIMERO MUSE\PRIMER CUATRI\AM1 - Ampliacion de Matematicas 1\Hitos_CN\Hito 7\Outputs\Heliocentric_hyperbolic_vels.txt';
```

### DESPUÉS (ruta adaptada al usuario actual):
```gmat
hyperbolic_vels.Filename = 'C:\RUTA\DEL\NUEVO\USUARIO\Hito 7\Outputs\Heliocentric_hyperbolic_vels.txt';
```

**IMPORTANTE:** 
- ✅ Solo cambia la RUTA ABSOLUTA
- ✅ El NOMBRE del archivo permanece idéntico
- ✅ Detecta automáticamente múltiples ReportFiles por script

## 🎮 Controles en la Interfaz

### Sidebar → Controles

1. **🔄 Reiniciar Aplicación**
   - Limpia caché y session_state
   - Reinicia la app

2. **🛠️ Reconfigurar Outputs** (NUEVO)
   - Fuerza reconfiguración de rutas
   - Útil si el usuario movió la carpeta del proyecto

## 🧪 Testing

Para probar el sistema:

```powershell
# Test completo (sin modificar archivos)
python streamlit_app/test_setup_outputs.py

# Cuando te pida, responde 'S' para ejecutar configuración
```

Tests incluidos:
1. ✅ Carpeta Outputs
2. ✅ Estado de Configuración
3. ✅ Archivos .script existen
4. ✅ Detección de ReportFiles
5. ✅ Configuración Completa
6. ✅ Verificación de Rutas

## 📊 Archivos .script Procesados

Total: **3 scripts, 6 ReportFiles**

1. **GMAT_AM1_Heliocentric.script**
   - `hyperbolic_vels.Filename` → `Outputs/Heliocentric_hyperbolic_vels.txt`
   - `final_results.Filename` → `Outputs/Heliocentric_final_results.txt`

2. **GMAT_AM1_transfer.script**
   - `hyperbolic_vels.Filename` → `Outputs/Transfer_hyperbolic_vels.txt`
   - `final_results.Filename` → `Outputs/Transfer_final_results.txt`

3. **PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script**
   - `hyperbolic_vels.Filename` → `Outputs/Plantilla_hyperbolic_vels.txt`
   - `final_results.Filename` → `Outputs/Plantilla_final_results.txt`

## ✨ Ventajas

✅ **Portabilidad Total:** Funciona en cualquier ubicación del sistema  
✅ **Cero Configuración Manual:** Todo automático  
✅ **Eficiente:** Solo se ejecuta una vez  
✅ **Reversible:** Permite reconfiguración si es necesario  
✅ **Transparente:** Logs detallados de todas las operaciones  
✅ **Seguro:** No modifica nombres, solo rutas  
✅ **Robusto:** Maneja múltiples ReportFiles por script  

## 🚀 Próximos Pasos para el Usuario

1. Ejecutar la aplicación normalmente:
   ```powershell
   streamlit run streamlit_app/main_app.py
   ```

2. La primera vez:
   - Verás logs de configuración en la consola
   - Se creará la carpeta `Outputs/`
   - Se actualizarán los 3 archivos `.script`

3. Ejecuciones posteriores:
   - Todo funciona sin configuración adicional

4. Si mueves la carpeta del proyecto:
   - Usa el botón "🛠️ Reconfigurar Outputs" en el sidebar

## 📖 Documentación

- **Documentación completa:** `OUTPUTS_CONFIG_README.md`
- **Tests:** `test_setup_outputs.py`
- **Código fuente:** `setup_outputs.py`

## 🐛 Troubleshooting

### Problema: "Script no encontrado"
**Solución:** Verifica que los archivos .script están en el directorio padre de `streamlit_app/`

### Problema: "Archivo de marca existe pero carpeta Outputs no"
**Solución:** Automático - se recrea la carpeta

### Problema: Quiero resetear
**Solución:** 
```powershell
del streamlit_app\.outputs_configured
streamlit run streamlit_app/main_app.py
```

---

## 🎉 Implementación Completada

El sistema está listo para usar. La próxima vez que ejecutes la aplicación, se configurará automáticamente sin intervención manual.
