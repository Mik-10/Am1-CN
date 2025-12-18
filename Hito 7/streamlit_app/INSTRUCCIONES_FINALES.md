# 🚀 INSTRUCCIONES FINALES - CONFIGURACIÓN ITY

## ✅ Cambios Implementados

Se ha actualizado completamente la GUI de Streamlit para trabajar con los nuevos scripts de misión ITY:

### Archivos Nuevos Creados
1. ✅ `ITY_mission.py` - Funciones de cálculo de misión
2. ✅ `gmat_backend_ITY.py` - Backend GMAT para ITY
3. ✅ `ejemplos_uso_ITY.py` - Ejemplos de código
4. ✅ `README.md` - Documentación unificada
5. ✅ `INICIO_RAPIDO_ITY.ps1` - Script de verificación e inicio
6. ✅ `RESUMEN_CAMBIOS_ITY.md` - Resumen detallado de cambios

### Archivos Modificados
1. ✅ `config.py` - Agregados nuevos nombres de scripts
2. ✅ `gui_components.py` - Nueva pestaña ITY
3. ✅ `main_app.py` - Integración de nueva pestaña

---

## 📋 PASOS SIGUIENTES (USUARIO)

### 1. Copiar Scripts GMAT ⚠️ IMPORTANTE

Los scripts GMAT deben estar en el **directorio padre** de `streamlit_app`:

```
Hito 7/
├── GMAT_ITY_Heliocentric.script    ← Copiar aquí
├── GMAT_ITY_transfer.script        ← Copiar aquí
└── streamlit_app/
    ├── main_app.py
    └── ...
```

**Comando para copiar (desde directorio Hito 7):**

```powershell
# Si los scripts están en otro lugar, ajusta la ruta
Copy-Item ".\GMAT_ITY_Heliocentric.script" -Destination "."
Copy-Item ".\GMAT_ITY_transfer.script" -Destination "."
```

---

### 2. Verificar Instalación

Ejecuta el script de verificación:

```powershell
cd streamlit_app
.\INICIO_RAPIDO_ITY.ps1
```

Esto verificará:
- ✓ Python 3.12
- ✓ Scripts GMAT en ubicación correcta
- ✓ GMAT R2025a instalado
- ✓ Dependencias Python
- ✓ Módulos ITY

---

### 3. Ejecutar la Aplicación

**Opción A: Con script de inicio**
```powershell
cd streamlit_app
.\INICIO_RAPIDO_ITY.ps1
```

**Opción B: Manual**
```powershell
cd streamlit_app
streamlit run main_app.py
```

---

### 4. Usar la Nueva Pestaña ITY

Una vez abierta la aplicación en el navegador:

1. **Ve a la pestaña**: 🚀 Misión ITY Mars-Earth

2. **Configura los parámetros**:
   - Época de misión (formato GMAT)
   - Duración del vuelo (días)
   - Órbita de salida (Mars): SMA, Inclinación, Excentricidad
   - Órbita de llegada (Earth): SMA, Inclinación, Excentricidad

3. **Ejecuta la misión**:
   - Click en "🚀 Ejecutar Misión Completa ITY"
   - Espera 1-3 minutos mientras se ejecutan las 3 fases

4. **Revisa los resultados**:
   - Velocidades hiperbólicas
   - Parámetros de Redson
   - Resultados finales de GMAT
   - Opcionalmente exporta a JSON

---

## 🔍 Verificación de Scripts GMAT

Asegúrate de que los scripts GMAT tienen los objetos necesarios:

### GMAT_ITY_Heliocentric.script debe tener:
- `heliocentric_SC` (spacecraft)
- `test` (spacecraft auxiliar)
- `FlightTime` (variable)
- Reporte que genera `hyperbolic_vels.txt`

### GMAT_ITY_transfer.script debe tener:
- `Sonda_Red_son` (spacecraft)
- `test` (spacecraft para conversión)
- `FlightTime` (variable)
- `C3E_Goal`, `Goal_BdotR`, `Goal_BdotT`, `Goal_SMA`, `Goal_ecc` (variables)
- `Half_Flight_Time` (variable)
- Reporte que genera `FinalResults.txt`

---

## 🐛 Troubleshooting

### Error: "Script heliocéntrico NO encontrado"

**Causa**: Los scripts no están en la ubicación correcta.

**Solución**:
```powershell
# Desde el directorio Hito 7
ls GMAT_ITY*.script

# Si no aparecen, cópialos desde donde estén
Copy-Item "ruta\origen\GMAT_ITY_Heliocentric.script" -Destination "."
Copy-Item "ruta\origen\GMAT_ITY_transfer.script" -Destination "."
```

---

### Error: "No se encuentra el archivo de inicio de GMAT"

**Causa**: GMAT no está instalado o está en otra ubicación.

**Solución**:
1. Verifica la instalación de GMAT en:
   ```
   C:\Users\mikde\GMAT_R2025a\
   ```

2. Si GMAT está en otra ubicación, edita `config.py`:
   ```python
   GMAT_INSTALL_PATH = r"C:\tu\ruta\GMAT_R2025a"
   ```

---

### Error: "ModuleNotFoundError"

**Causa**: Dependencias no instaladas.

**Solución**:
```powershell
cd streamlit_app
pip install -r requirements.txt
```

---

### GMAT no converge o se congela

**Causa**: Parámetros orbitales incompatibles o solver tiene problemas.

**Solución**:
1. Usa parámetros por defecto primero
2. Verifica el log: `GMAT_ITY_Log.txt`
3. Reduce la duración del vuelo
4. Ajusta las excentricidades
5. Verifica que los scripts GMAT son correctos

---

### No se muestran resultados

**Causa**: GMAT no generó los archivos de salida.

**Solución**:
1. Verifica que existen:
   - `hyperbolic_vels.txt`
   - `FinalResults.txt`

2. Revisa el log de GMAT

3. Verifica que los scripts tienen configurados los reportes

---

## 📚 Documentación Adicional

### Archivos de Documentación
- `README.md` - Documentación unificada del proyecto
- `IMPLEMENTACION_OUTPUTS.md` - Detalles de configuración de outputs
- `ejemplos_uso_ITY.py` - Ejemplos de código Python

### Estructura de Archivos de Salida

**hyperbolic_vels.txt** (generado por script heliocéntrico):
```
[Fecha] [Hora] [Vx] [Vy] [Vz]
...
```

**FinalResults.txt** (generado por script transferencia):
```
[Header con nombres de columnas]
[Datos finales del spacecraft]
```

---

## 🎯 Ejemplo de Uso Completo

### 1. Desde Python (sin GUI):

```python
from ITY_mission import MissionConfig
from gmat_backend_ITY import ITYMission

# Configuración
config = MissionConfig(
    mission_epoch="06 Jun 2026 11:59:28.000",
    flight_duration=350,
    sma_dep=6500,
    sma_arr=31780,
    inc_dep=50,
    inc_arr=80
)

# Crear misión
mission = ITYMission(
    script_helio_path="../GMAT_ITY_Heliocentric.script",
    script_transfer_path="../GMAT_ITY_transfer.script",
    mission_config=config
)

# Ejecutar
results = mission.run_complete_mission()

# Ver resultados
print(results)
```

### 2. Desde GUI (Streamlit):

1. Ejecutar: `streamlit run main_app.py`
2. Abrir pestaña "🚀 Misión ITY Mars-Earth"
3. Configurar parámetros en la interfaz
4. Click "Ejecutar Misión Completa ITY"
5. Ver resultados en pantalla

---

## ✅ Checklist Final

Antes de ejecutar, verifica:

- [ ] Python 3.12 instalado
- [ ] Scripts GMAT en directorio correcto (padre de streamlit_app)
- [ ] GMAT R2025a instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `api_startup_file.txt` existe en GMAT/bin
- [ ] Los scripts GMAT tienen los objetos necesarios

---

## 🎉 ¡Listo para Usar!

Si todos los pasos anteriores están completos, la aplicación debería funcionar correctamente.

Para cualquier problema, revisa:
1. Los logs en la terminal
2. `GMAT_ITY_Log.txt`
3. La documentación en `README_ITY.md`
4. Los ejemplos en `ejemplos_uso_ITY.py`

---

**¡Buena suerte con tu misión Mars-Earth! 🚀**

### Nota sobre RAAN y AOP

Los parámetros `RAAN` y `AOP` se muestran en la app tras completar la Fase 3 (transferencia). Se obtienen automáticamente desde GMAT al convertir desde `OutgoingAsymptote` a `Keplerian`.

_Última actualización: 17 de diciembre de 2025_
