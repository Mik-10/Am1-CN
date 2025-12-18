# 🔧 Sistema de Configuración Automática de Outputs

## ¿Qué hace este sistema?

Cuando ejecutas la aplicación **por primera vez**, se configura automáticamente:

1. **Crea la carpeta `Outputs`** en el directorio padre (si no existe)
2. **Actualiza todos los archivos `.script`** de GMAT para que apunten a esta carpeta
3. **Guarda la configuración** para no repetir el proceso en futuros arranques

## Archivos involucrados

### `setup_outputs.py`
Módulo que contiene toda la lógica de configuración:
- `check_and_setup_if_needed()`: Verifica si es primera instalación y configura si es necesario
- `setup_outputs()`: Realiza la configuración completa
- `force_reconfigure()`: Fuerza una reconfiguración (útil si moviste la carpeta)

### `.outputs_configured`
Archivo de marca (se crea automáticamente) que indica que ya se realizó la configuración.
- Se crea en: `streamlit_app/.outputs_configured`
- Si lo eliminas, la configuración se ejecutará nuevamente

## Scripts que se actualizan

Los siguientes archivos `.script` se modifican automáticamente:

1. **GMAT_AM1_Heliocentric.script**
   - `hyperbolic_vels.Filename`
   - `final_results.Filename`

2. **GMAT_AM1_transfer.script**
   - `hyperbolic_vels.Filename`
   - `final_results.Filename`

3. **PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script**
   - `hyperbolic_vels.Filename`
   - `final_results.Filename`

## ¿Qué se modifica exactamente?

### ANTES (ruta hardcoded del usuario original):
```gmat
hyperbolic_vels.Filename = 'C:\Users\mikde\Desktop\ETSIAE\MUSE\11 - PRIMERO MUSE\PRIMER CUATRI\AM1 - Ampliacion de Matematicas 1\Hitos_CN\Hito 7\Outputs\Heliocentric_hyperbolic_vels.txt';
```

### DESPUÉS (ruta adaptada al usuario actual):
```gmat
hyperbolic_vels.Filename = 'C:\TU\RUTA\AL\Hito 7\Outputs\Heliocentric_hyperbolic_vels.txt';
```

**IMPORTANTE:** Solo se cambia la **RUTA ABSOLUTA**, el **nombre del archivo** permanece igual.

## Flujo de ejecución

```
1. Usuario ejecuta: streamlit run main_app.py
   ↓
2. main_app.py importa setup_outputs
   ↓
3. check_and_setup_if_needed() verifica:
   ¿Existe .outputs_configured?
   ├─ SÍ → Ya está configurado ✅
   └─ NO → Primera instalación, ejecutar setup_outputs()
   ↓
4. setup_outputs():
   ├─ Crear carpeta Outputs/ (si no existe)
   ├─ Leer cada .script
   ├─ Encontrar líneas con .Filename =
   ├─ Actualizar rutas manteniendo nombres
   └─ Guardar .script modificados
   ↓
5. Crear archivo .outputs_configured
   ↓
6. Aplicación lista para usar ✅
```

## Casos de uso

### Primer arranque
```bash
streamlit run main_app.py
```
- Se ejecuta configuración automática
- Se crean/actualizan archivos
- Se muestra en logs: "🆕 Primera instalación detectada, configurando..."

### Arranques posteriores
```bash
streamlit run main_app.py
```
- No se ejecuta configuración
- Se muestra en logs: "✅ Outputs ya configurados previamente"

### Usuario movió la carpeta del proyecto
```bash
# Opción 1: Desde la interfaz
→ Click en "🛠️ Reconfigurar Outputs" (sidebar)

# Opción 2: Manualmente
→ Eliminar: streamlit_app/.outputs_configured
→ streamlit run main_app.py
```

### Desarrollador quiere forzar reconfiguración
```python
from setup_outputs import force_reconfigure

force_reconfigure()
```

## Logs de ejemplo

### Primera instalación exitosa:
```
======================================================================
🔧 CONFIGURACIÓN INICIAL - CARPETA OUTPUTS
======================================================================

✅ Carpeta Outputs creada en: C:\TU\RUTA\Hito 7\Outputs

📝 Actualizando archivos .script...
📄 Procesando GMAT_AM1_Heliocentric.script...
   Encontrados 2 ReportFile(s)
   ✅ hyperbolic_vels: Heliocentric_hyperbolic_vels.txt
   ✅ final_results: Heliocentric_final_results.txt
   💾 GMAT_AM1_Heliocentric.script actualizado correctamente

📄 Procesando GMAT_AM1_transfer.script...
   Encontrados 2 ReportFile(s)
   ✅ hyperbolic_vels: Transfer_hyperbolic_vels.txt
   ✅ final_results: Transfer_final_results.txt
   💾 GMAT_AM1_transfer.script actualizado correctamente

📄 Procesando PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script...
   Encontrados 2 ReportFile(s)
   ✅ hyperbolic_vels: Plantilla_hyperbolic_vels.txt
   ✅ final_results: Plantilla_final_results.txt
   💾 PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script actualizado correctamente

✅ Configuración marcada como completada

======================================================================
✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE
======================================================================
```

### Arranque posterior:
```
✅ Outputs ya configurados previamente
```

## Solución de problemas

### Error: "Script no encontrado"
**Causa:** El script .script no está en el directorio esperado
**Solución:** Verifica que los archivos están en el directorio padre de `streamlit_app/`

### Error: "No se pudo actualizar ReportFile"
**Causa:** El formato de la línea `.Filename =` es diferente al esperado
**Solución:** 
1. Abre el archivo .script manualmente
2. Verifica que la línea tenga formato: `nombre.Filename = 'ruta';`
3. Si el formato es correcto, revisa los logs para más detalles

### La carpeta Outputs fue eliminada
**Solución automática:** Al iniciar la app, se detecta y se recrea automáticamente

### Quiero resetear la configuración
**Opción 1 (UI):**
1. Sidebar → "🛠️ Reconfigurar Outputs"
2. Reiniciar aplicación

**Opción 2 (Manual):**
```bash
# Eliminar archivo de marca
del streamlit_app\.outputs_configured

# Reiniciar aplicación
streamlit run main_app.py
```

## Ventajas de este sistema

✅ **Portabilidad:** La app funciona en cualquier ubicación del sistema  
✅ **Automático:** No requiere configuración manual del usuario  
✅ **Seguro:** No se ejecuta innecesariamente en cada arranque  
✅ **Flexible:** Permite reconfiguración manual si es necesario  
✅ **Transparente:** Logs detallados de todas las operaciones  
✅ **No invasivo:** Solo modifica las rutas, mantiene nombres de archivos  

## Integración con el resto de la aplicación

Los módulos que leen los archivos de output (`am1_mission.py`, `gmat_backend_am1.py`) ya están configurados para buscar en la carpeta `Outputs/`:

```python
# am1_mission.py
outputs_dir = os.path.join(os.path.dirname(__file__), "..", "Outputs")
full_path = os.path.join(outputs_dir, file_path)
```

Esto asegura consistencia en toda la aplicación.
