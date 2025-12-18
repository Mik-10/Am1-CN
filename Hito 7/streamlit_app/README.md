# 🚀 Aplicación ITY: Misiones Interplanetarias Mars–Earth

Interfaz en Streamlit para optimizar misiones Mars–Earth con GMAT R2025a, incluyendo análisis Porkchop y ejecución en dos fases (heliocéntrica + transferencia) con parámetros de Redson.

## ✨ Características

- Fase Heliocéntrica: cálculo de V∞ de salida y llegada
- Fase de Transferencia: B-Plane targets y conversión a keplerianos
- Parámetros de Redson: C3, RHA, DHA, BVAZI, BdotT, BdotR, RAAN, AOP
- Integración con GMAT R2025a y lectura de outputs
- UI con progreso, logs y exportación a JSON

## 🔧 Requisitos

- Windows + PowerShell
- Python 3.12
- GMAT R2025a en `C:\Users\mikde\GMAT_R2025a` (o ajusta `config.py`)
- Scripts GMAT en el directorio padre de `streamlit_app`:
  - `GMAT_ITY_Heliocentric.script`
  - `GMAT_ITY_transfer.script`

## 🚀 Inicio Rápido

```powershell
# 1) Crear y activar venv
py -3.12 -m venv venv; .\venv\Scripts\Activate.ps1

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Ejecutar
streamlit run main_app.py
```

Alternativa en Windows:

```powershell
.\EJECUTAR_APP.ps1
```

## 📁 Estructura del Proyecto

```
streamlit_app/
├── main_app.py               # App principal (Streamlit)
├── gui_components.py         # Componentes UI
├── gmat_backend_ity.py       # Backend GMAT (ITY)
├── ity_mission.py            # Cálculos (Redson, B-Plane)
├── porkchop_manager.py       # Diagrama Porkchop
├── setup_outputs.py          # Configuración outputs
├── IMPLEMENTACION_OUTPUTS.md # Documentación outputs
├── OUTPUTS_CONFIG_README.md  # Guía rápida outputs
├── requirements.txt
└── README.md                 # Este archivo
```

## 🧭 Uso en la App

1. Pestaña Porkchop (opcional): genera diagrama y busca ventanas
2. Pestaña “Misión ITY Mars–Earth”:
   - Configura época y duración del vuelo
   - Configura órbitas de salida/llegada
   - Ejecuta misión completa (3 fases)
   - Revisa resultados: V∞, C3, RHA, DHA, BVAZI, BdotT, BdotR y, tras la transferencia, RAAN y AOP

## 🧩 Módulos Clave

- `ity_mission.py`: `MissionConfig`, `calculate_redson_parameters()`
- `gmat_backend_ity.py`: `ITYMission` con `run_heliocentric_mission()`, `calculate_transfer_parameters()`, `run_transfer_mission()` y `run_complete_mission()`
- `gui_components.py`: `render_ITY_mission_tab()` y vistas auxiliares

## 🐛 Troubleshooting

- GMAT no arranca: verifica `C:\Users\mikde\GMAT_R2025a\bin\api_startup_file.txt`
- Scripts no encontrados: copia `GMAT_ITY_*.script` al directorio padre de `streamlit_app`
- Resultados vacíos: asegúrate de que se generan `hyperbolic_vels.txt` y `FinalResults.txt`
- Convergencia: prueba con parámetros por defecto o reduce la duración

## 📝 Notas

- Evita tildes/espacios en rutas; usa rutas simples
- RAAN y AOP se obtienen de GMAT en la Fase 3 (transferencia)

---

Proyecto académico – ETSIAE MUSE | Última actualización: 17/12/2025
