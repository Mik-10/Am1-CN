"""
Porkchop Plot Manager Module
Maneja la lógica de cálculo y visualización de diagramas Porkchop.

Notas Técnicas:
- Usa matplotlib para compatibilidad con el código existente
- Retorna figuras para integración en Streamlit (no usa plt.show())
- Lee datos del formato GMAT: DELTA_V_PORKCHOP.txt
- Columnas GMAT esperadas: JD, TFO, ImpulsiveBurn1.Element1/2/3, Add_V
- Formato: delimitado por espacios (whitespace-separated)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from scipy.interpolate import griddata
from typing import Optional, Tuple
import logging

# Configuración de logging
logger = logging.getLogger(__name__)


class PorkchopManager:
    """
    Clase para generar diagramas Porkchop a partir de datos de trayectorias.
    
    Un diagrama Porkchop muestra:
    - Eje X: Fecha de lanzamiento
    - Eje Y: Fecha de llegada
    - Contornos: DeltaV total requerido
    - Líneas adicionales: Tiempo de vuelo (ToF) constante
    """
    
    def __init__(self, data_file: str):
        """
        Inicializa el manager con un archivo de datos.
        
        Args:
            data_file: Ruta al archivo CSV con los resultados de porkchop
        """
        self.data_file = data_file
        self.datos = None
        self._load_data()
    
    def _load_data(self):
        """Carga y valida los datos del archivo DELTA_V_PORKCHOP.txt."""
        try:
            # Cargar datos del formato GMAT: JD, TFO, ImpulsiveBurn1.Element1/2/3, Add_V
            # Usar delimitador de espacios múltiples (whitespace)
            # Usar separador regex de espacios para evitar FutureWarning de pandas
            self.datos = pd.read_csv(self.data_file, sep=r"\s+")
            
            logger.info(f"Datos cargados: {len(self.datos)} filas")
            logger.info(f"Columnas detectadas: {self.datos.columns.tolist()}")
            
            # Mapeo de columnas del formato GMAT al formato interno
            column_mapping = {
                'JD': 'Start_MJD',
                'TFO': 'Duration',
                'ImpulsiveBurn1.Element1': 'Vx',
                'ImpulsiveBurn1.Element2': 'Vy',
                'ImpulsiveBurn1.Element3': 'Vz',
                'Add_V': 'DeltaV'
            }
            
            # Validar que existen las columnas del formato GMAT
            required_gmat_cols = list(column_mapping.keys())
            missing_cols = [col for col in required_gmat_cols if col not in self.datos.columns]
            
            if missing_cols:
                raise ValueError(
                    f"Archivo con formato incorrecto. Columnas GMAT faltantes: {missing_cols}\n"
                    f"Columnas encontradas: {self.datos.columns.tolist()}"
                )
            
            # Renombrar columnas al formato interno estándar
            self.datos = self.datos.rename(columns=column_mapping)
            
            # Convertir columnas numéricas
            numeric_cols = ['Start_MJD', 'Duration', 'Vx', 'Vy', 'Vz', 'DeltaV']
            for col in numeric_cols:
                self.datos[col] = pd.to_numeric(self.datos[col], errors='coerce')
            
            # Eliminar filas con valores NaN
            rows_before = len(self.datos)
            self.datos = self.datos.dropna(subset=numeric_cols)
            rows_after = len(self.datos)
            
            if rows_before > rows_after:
                logger.warning(f"⚠️ Se eliminaron {rows_before - rows_after} filas con datos inválidos")
            
            # DeltaV ya viene calculado en el archivo, pero verificar con el cálculo
            calculated_deltav = np.sqrt(
                self.datos['Vx']**2 + 
                self.datos['Vy']**2 + 
                self.datos['Vz']**2
            )
            
            # Usar el DeltaV del archivo (Add_V) que es más preciso
            logger.info(f"Rango de DeltaV: {self.datos['DeltaV'].min():.2f} - {self.datos['DeltaV'].max():.2f} km/s")
            
        except Exception as e:
            logger.error(f"Error al cargar datos: {str(e)}")
            raise
    
    @staticmethod
    def mjd_to_date_vectorized(mjd_array, base_mjd=31136.999630, base_date_str='2026-04-06'):
        """
        Convierte Modified Julian Date (MJD) a fechas de Python.
        
        Args:
            mjd_array: Array de valores MJD
            base_mjd: MJD de referencia
            base_date_str: Fecha gregoriana correspondiente al base_mjd
            
        Returns:
            Array de objetos datetime
        """
        base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
        delta_days_func = np.vectorize(
            lambda mjd: base_date + timedelta(days=mjd - base_mjd)
        )
        return delta_days_func(mjd_array)
    
    def get_porkchop_figure(
        self, 
        deltav_min: float = None,
        deltav_max: float = 13.0,
        deltav_step: float = 0.20,
        tof_levels: list = None,
        figsize: Tuple[int, int] = (10, 10)
    ) -> plt.Figure:
        """
        Genera la figura del diagrama Porkchop.
        
        Args:
            deltav_min: DeltaV mínimo para contornos (km/s). Si es None, se calcula automáticamente
            deltav_max: DeltaV máximo para contornos (km/s)
            deltav_step: Paso entre contornos (km/s)
            tof_levels: Lista de niveles de Time of Flight (días). Default: [290, 310, 330, 350, 370]
            figsize: Tamaño de la figura (ancho, alto)
            
        Returns:
            Figura de matplotlib lista para mostrar
        """
        if self.datos is None or len(self.datos) == 0:
            raise ValueError("No hay datos cargados para generar el diagrama")
        
        if tof_levels is None:
            tof_levels = [290, 310, 330, 350, 370]
        
        # Calcular fecha de llegada en MJD
        self.datos['Fecha_Llegada_MJD'] = self.datos['Start_MJD'] + self.datos['Duration']
        
        # Puntos dispersos (X=Lanzamiento, Y=Llegada, Z=DeltaV)
        X_scat = self.datos['Start_MJD'].values
        Y_scat = self.datos['Fecha_Llegada_MJD'].values
        Z_scat = self.datos['DeltaV'].values
        
        # Definir malla regular para interpolación (mayor resolución)
        xi_mjd = np.linspace(X_scat.min(), X_scat.max(), 300)
        yi_mjd = np.linspace(Y_scat.min(), Y_scat.max(), 300)
        
        # Crear malla 2D
        XI, YI = np.meshgrid(xi_mjd, yi_mjd)
        
        # Interpolación cúbica
        ZI = griddata((X_scat, Y_scat), Z_scat, (XI, YI), method='cubic')
        
        # Convertir coordenadas MJD a fechas de matplotlib
        XI_dates = self.mjd_to_date_vectorized(xi_mjd)
        YI_dates = self.mjd_to_date_vectorized(yi_mjd)
        XI_num = mdates.date2num(XI_dates)
        YI_num = mdates.date2num(YI_dates)
        
        # ====================================================================
        # GENERAR FIGURA
        # ====================================================================
        fig = plt.figure(figsize=figsize)
        
        # Calcular niveles de contorno automáticamente desde los datos
        min_val = np.floor(np.nanmin(Z_scat))
        max_val = deltav_max
        levels_c = np.arange(min_val, max_val, 0.15)
        
        # a) Líneas de contorno de DeltaV con etiquetas
        c = plt.contour(XI_num, YI_num, ZI, levels=levels_c, 
                        cmap='viridis_r', linewidths=1.5)
        plt.clabel(c, inline=True, fontsize=8, fmt='%1.1f')
        
        # b) Líneas de Duración Constante (Time of Flight)
        for duration in tof_levels:
            plt.plot(XI_num, XI_num + duration, 'r--', linewidth=0.8, alpha=0.7)
        
        # Barra de color
        plt.colorbar(c, label=r'$\Delta V$ (km/s)')
        
        ax = plt.gca()
        
        # Formato de ejes de fecha con localizador cada 15 días
        loc_x = mdates.DayLocator(interval=15)
        ax.xaxis.set_major_locator(loc_x)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
        
        loc_y = mdates.DayLocator(interval=30)
        ax.yaxis.set_major_locator(loc_y)
        ax.yaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
        ax.tick_params(axis='y', rotation=45, labelsize=8)
        plt.setp(ax.yaxis.get_majorticklabels(), ha='right')
        
        # Títulos y etiquetas
        plt.title('Diagrama Porkchop Marte-Tierra', fontsize=20, pad=15)
        plt.xlabel('Fecha de Lanzamiento', fontsize=10, fontweight='bold')
        plt.ylabel('Fecha de Llegada', fontsize=10, fontweight='bold')
        plt.grid(True, linestyle=':', alpha=0.5)
        
        plt.tight_layout()
        
        logger.info("✅ Diagrama Porkchop generado")
        
        return fig
    
    def save_porkchop(
        self, 
        output_file: str = 'diagrama_porkchop.png',
        **kwargs
    ):
        """
        Genera y guarda el diagrama Porkchop en un archivo.
        
        Args:
            output_file: Ruta del archivo de salida
            **kwargs: Argumentos adicionales para get_porkchop_figure()
        """
        fig = self.get_porkchop_figure(**kwargs)
        fig.savefig(output_file, dpi=150, bbox_inches='tight')
        logger.info(f"✅ Diagrama guardado en: {output_file}")
        plt.close(fig)
    
    def get_optimal_launch_window(self, max_deltav: float = 8.0) -> pd.DataFrame:
        """
        Encuentra las ventanas de lanzamiento óptimas (menor DeltaV).
        
        Args:
            max_deltav: DeltaV máximo aceptable (km/s)
            
        Returns:
            DataFrame con las mejores opciones ordenadas por DeltaV
        """
        if self.datos is None:
            return pd.DataFrame()
        
        # Filtrar por DeltaV máximo
        filtered = self.datos[self.datos['DeltaV'] <= max_deltav].copy()
        
        # Ordenar por DeltaV
        optimal = filtered.sort_values('DeltaV').head(10)
        
        logger.info(f"Se encontraron {len(optimal)} ventanas óptimas")
        
        return optimal


# ============================================================================
# FUNCIÓN PRINCIPAL PARA LA GUI
# ============================================================================

def get_porkchop_figure(
    data_file: str,
    deltav_min: float = 6.0,
    deltav_max: float = 13.0,
    deltav_step: float = 0.5,
    tof_levels: list = None
) -> plt.Figure:
    """
    Función simplificada para uso directo en la GUI de Streamlit.
    
    Args:
        data_file: Ruta al archivo CSV con datos
        deltav_min: DeltaV mínimo para contornos (km/s)
        deltav_max: DeltaV máximo para contornos (km/s)
        deltav_step: Paso entre contornos (km/s)
        tof_levels: Lista de niveles de ToF (días)
        
    Returns:
        Figura de matplotlib
    """
    manager = PorkchopManager(data_file)
    return manager.get_porkchop_figure(
        deltav_min=deltav_min,
        deltav_max=deltav_max,
        deltav_step=deltav_step,
        tof_levels=tof_levels
    )


# ============================================================================
# EJEMPLO DE USO
# ============================================================================
if __name__ == "__main__":
    # Solo se ejecuta si se corre este archivo directamente
    try:
        data_file = '..\\DELTA_V_PORKCHOP.txt'
        
        # Crear manager
        manager = PorkchopManager(data_file)
        
        # Generar diagrama
        fig = manager.get_porkchop_figure()
        
        # Guardar
        manager.save_porkchop('test_porkchop.png')
        
        # Buscar ventanas óptimas
        optimal = manager.get_optimal_launch_window(max_deltav=8.0)
        print("\n=== VENTANAS ÓPTIMAS ===")
        print(optimal[['Start_MJD', 'Duration', 'DeltaV']].head())
        
    except Exception as e:
        logger.error(f"Error en ejemplo: {e}")
