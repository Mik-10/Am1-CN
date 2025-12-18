"""
Generador de Scripts GMAT Personalizados
Crea archivos .script basados en la plantilla con valores calculados por el usuario.
"""

import os
import re
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class GmatScriptGenerator:
    """
    Generador de scripts GMAT personalizados basados en plantilla.
    """
    
    def __init__(self, template_path: str):
        """
        Inicializa el generador con una plantilla.
        
        Args:
            template_path: Ruta al archivo .script plantilla
        """
        self.template_path = Path(template_path)
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
        
        # Leer plantilla
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template_content = f.read()
        
        logger.info(f"Plantilla cargada: {self.template_path.name}")
    
    def generate_script(
        self,
        mission_epoch: str,
        flight_duration: float,
        sma_dep: float,
        ecc_dep: float,
        inc_dep: float,
        c3_goal: float,
        bdot_r: float,
        bdot_t: float,
        raan: float = None,
        aop: float = None,
        goal_sma: float = None,
        goal_ecc: float = None,
        output_filename: str = None
    ) -> str:
        """
        Genera un script GMAT personalizado con los valores calculados.
        
        Args:
            mission_epoch: Época de la misión (ej: '06 Jun 2026 11:59:28.000')
            flight_duration: Duración del vuelo en días
            sma_dep: Semi-major axis de salida (km)
            ecc_dep: Excentricidad de salida
            inc_dep: Inclinación de salida (grados)
            c3_goal: Energía característica C3 (km²/s²)
            bdot_r: Componente R del B-Plane (km)
            bdot_t: Componente T del B-Plane (km)
            raan: Right Ascension of Ascending Node (grados) - opcional
            aop: Argument of Periapsis (grados) - opcional
            goal_sma: Semi-major axis objetivo de llegada (km) - opcional
            goal_ecc: Excentricidad objetivo de llegada - opcional
            output_filename: Nombre del archivo de salida (si None, retorna string)
            
        Returns:
            Contenido del script generado (string)
        """
        content = self.template_content
        
        logger.info("Generando script personalizado...")
        logger.info(f"  Época: {mission_epoch}")
        logger.info(f"  Duración: {flight_duration} días")
        logger.info(f"  SMA: {sma_dep} km, ECC: {ecc_dep}, INC: {inc_dep}°")
        logger.info(f"  C3: {c3_goal:.4f} km²/s²")
        logger.info(f"  B-Plane: R={bdot_r:.2f} km, T={bdot_t:.2f} km")
        
        # ====================================================================
        # Reemplazar épocas en TODOS los spacecrafts
        # ====================================================================
        
        # Época: heliocentric_SC, test, Sonda_Red_son
        content = self._replace_spacecraft_parameter(
            content,
            'heliocentric_SC',
            'Epoch',
            f"'{mission_epoch}'"
        )
        content = self._replace_spacecraft_parameter(
            content,
            'test',
            'Epoch',
            f"'{mission_epoch}'"
        )
        content = self._replace_spacecraft_parameter(
            content,
            'Sonda_Red_son',
            'Epoch',
            f"'{mission_epoch}'"
        )
        
        # ====================================================================
        # Reemplazar parámetros orbitales en 'test' (órbita hiperbólica de salida)
        # ====================================================================
        
        # Semi-major axis
        content = self._replace_spacecraft_parameter(
            content,
            'test',
            'SMA',
            str(sma_dep)
        )
        
        # Excentricidad
        content = self._replace_spacecraft_parameter(
            content,
            'test',
            'ECC',
            str(ecc_dep)
        )
        
        # Inclinación
        content = self._replace_spacecraft_parameter(
            content,
            'test',
            'INC',
            str(inc_dep)
        )
        
        # RAAN (si se proporciona)
        if raan is not None:
            content = self._replace_spacecraft_parameter(
                content,
                'test',
                'RAAN',
                str(raan)
            )
            # También actualizar Sonda_Red_son.RAAN
            content = self._replace_spacecraft_parameter(
                content,
                'Sonda_Red_son',
                'RAAN',
                str(raan)
            )
        
        # AOP (si se proporciona)
        if aop is not None:
            content = self._replace_spacecraft_parameter(
                content,
                'test',
                'AOP',
                str(aop)
            )
        
        # ====================================================================
        # Reemplazar parámetros en 'Sonda_Red_son' (estado inicial en Marte)
        # ====================================================================
        
        # INC debe coincidir con test
        content = self._replace_spacecraft_parameter(
            content,
            'Sonda_Red_son',
            'INC',
            str(inc_dep)
        )
        
        # Si hay una órbita de parking (ECC cercana a 0, SMA positivo > 3396 km = radio Marte)
        # actualizamos Sonda_Red_son.SMA con el valor de salida
        # Nota: Las órbitas hiperbólicas tienen SMA negativo
        if sma_dep > 3396 and ecc_dep < 0.1:  # Órbita circular/elíptica de parking
            content = self._replace_spacecraft_parameter(
                content,
                'Sonda_Red_son',
                'SMA',
                str(sma_dep)
            )
            content = self._replace_spacecraft_parameter(
                content,
                'Sonda_Red_son',
                'ECC',
                str(ecc_dep)
            )
            logger.info(f"✓ Actualizando Sonda_Red_son con órbita de parking: SMA={sma_dep} km, ECC={ecc_dep}")
        
        # ====================================================================
        # Reemplazar variables de misión
        # ====================================================================
        
        # FlightTime
        content = self._replace_variable(
            content,
            'FlightTime',
            str(flight_duration)
        )
        
        # C3E_Goal
        content = self._replace_variable(
            content,
            'C3E_Goal',
            f"{c3_goal:.14f}"
        )
        
        # Half_Flight_Time
        half_flight = flight_duration / 2
        content = self._replace_variable(
            content,
            'Half_Flight_Time',
            str(half_flight)
        )
        
        # Goal_BdotR
        content = self._replace_variable(
            content,
            'Goal_BdotR',
            f"{bdot_r:.14f}"
        )
        
        # Goal_BdotT
        content = self._replace_variable(
            content,
            'Goal_BdotT',
            f"{bdot_t:.14f}"
        )
        
        # Goal_SMA (si se proporciona)
        if goal_sma is not None:
            content = self._replace_variable(
                content,
                'Goal_SMA',
                str(goal_sma)
            )
        
        # Goal_ecc (si se proporciona)
        if goal_ecc is not None:
            content = self._replace_variable(
                content,
                'Goal_ecc',
                str(goal_ecc)
            )
        
        logger.info("✅ Script generado exitosamente")
        
        # Guardar si se especifica nombre de archivo
        if output_filename:
            output_path = Path(output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"💾 Script guardado en: {output_path}")
        
        return content
    
    def _replace_spacecraft_parameter(self, content: str, spacecraft_name: str, param_name: str, new_value: str) -> str:
        """
        Reemplaza un parámetro de un spacecraft específico.
        
        Args:
            content: Contenido del script
            spacecraft_name: Nombre del spacecraft (ej: 'test', 'heliocentric_SC', 'Sonda_Red_son')
            param_name: Nombre del parámetro (ej: 'SMA', 'ECC', 'INC', 'Epoch')
            new_value: Nuevo valor
            
        Returns:
            Contenido modificado
        """
        # Patrón: spacecraft.PARAM = valor;
        # Nota: re.MULTILINE permite que ^ y $ coincidan con inicio/fin de línea
        pattern = rf"^({spacecraft_name}\.{param_name}\s*=\s*)([^;]+)(;)"
        replacement = rf"\g<1>{new_value}\g<3>"
        
        # Contar reemplazos
        new_content, num_replacements = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        
        if num_replacements == 0:
            logger.warning(f"⚠️ No se encontró {spacecraft_name}.{param_name} para reemplazar")
        else:
            logger.info(f"✓ {spacecraft_name}.{param_name} = {new_value}")
        
        return new_content
    
    def _replace_variable(self, content: str, var_name: str, new_value: str) -> str:
        """
        Reemplaza el valor de una variable GMAT.
        
        Args:
            content: Contenido del script
            var_name: Nombre de la variable (ej: 'FlightTime', 'C3E_Goal')
            new_value: Nuevo valor
            
        Returns:
            Contenido modificado
        """
        # Patrón: VARIABLE = valor;
        # Usamos ^ para asegurar que es inicio de línea (no un parámetro de spacecraft)
        pattern = rf"^({var_name}\s*=\s*)([^;]+)(;)"
        replacement = rf"\g<1>{new_value}\g<3>"
        
        # Contar reemplazos
        new_content, num_replacements = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        
        if num_replacements == 0:
            logger.warning(f"⚠️ No se encontró {var_name} para reemplazar")
        else:
            logger.info(f"✓ {var_name} = {new_value}")
        
        return new_content
    
    def generate_from_mission_results(
        self,
        mission_config: Dict,
        redson_params: Dict,
        output_filename: str = None
    ) -> str:
        """
        Genera script desde resultados de misión completos.
        
        Args:
            mission_config: Dict con configuración de misión (de MissionConfig.to_dict())
            redson_params: Dict con parámetros de Redson calculados
            output_filename: Nombre del archivo de salida (opcional)
            
        Returns:
            Contenido del script generado
        """
        return self.generate_script(
            mission_epoch=mission_config['mission_epoch'],
            flight_duration=mission_config['flight_duration'],
            sma_dep=mission_config['sma_dep'],
            ecc_dep=mission_config['ecc_dep'],
            inc_dep=mission_config['inc_dep'],
            c3_goal=redson_params['C3'],
            bdot_r=redson_params['BdotR'],
            bdot_t=redson_params['BdotT'],
            raan=redson_params.get('RAAN'),
            aop=redson_params.get('AOP'),
            goal_sma=mission_config.get('sma_arr'),
            goal_ecc=mission_config.get('ecc_arr'),
            output_filename=output_filename
        )


# ============================================================================
# FUNCIÓN DE CONVENIENCIA PARA STREAMLIT
# ============================================================================

def generate_custom_script_from_results(
    template_path: str,
    mission_config: Dict,
    redson_params: Dict
) -> str:
    """
    Función simplificada para uso en Streamlit.
    
    Args:
        template_path: Ruta a la plantilla
        mission_config: Configuración de misión
        redson_params: Parámetros de Redson
        
    Returns:
        Contenido del script generado (string)
    """
    generator = GmatScriptGenerator(template_path)
    return generator.generate_from_mission_results(
        mission_config=mission_config,
        redson_params=redson_params
    )


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Ejemplo de uso
    template = "../PLANTILLA_TRANSFERENCIA_MARTE_TIERRA.script"
    
    generator = GmatScriptGenerator(template)
    
    # Valores de ejemplo (como los que estarían en la plantilla)
    script_content = generator.generate_script(
        mission_epoch='06 Jun 2026 11:59:28.000',
        flight_duration=350,
        sma_dep=-3490.576340345992,
        ecc_dep=2.862156665893941,
        inc_dep=50.00000000012872,
        c3_goal=12.26969705922953,
        bdot_r=22882.23838266063,
        bdot_t=4288.708051212489,
        raan=269.47985183165,
        aop=278.6924689891934,
        output_filename="Mi_Mision_Personalizada.script"
    )
    
    print("\n✅ Script generado exitosamente")
    print(f"Longitud: {len(script_content)} caracteres")
