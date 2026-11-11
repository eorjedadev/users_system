"""
MÓDULO REUTILIZABLE: app.services.settings_service

DESCRIPCIÓN:
    Servicio de configuración local para gestionar los datos de contacto
    de los destinatarios de los reportes (Jefe y Encargado).

RESPONSABILIDAD:
    - Leer y persistir de forma segura en la tabla app_settings de SQLite
      los correos y números de WhatsApp del Jefe y Encargado.
"""

from typing import Dict
from app.models.database import DatabaseManager
from app.utils.logger import get_logger

logger = get_logger("settings_service")


class SettingsService:
    """Servicio para la persistencia y lectura de parámetros de destinatarios."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_recipients_settings(self) -> Dict[str, str]:
        """
        Retorna un diccionario con los datos configurados para Jefe y Encargado.
        """
        defaults = {
            "boss_name": "Jefe Directo",
            "boss_email": "",
            "boss_phone": "",
            "supervisor_name": "Encargado",
            "supervisor_email": "",
            "supervisor_phone": "",
            "preferred_browser": "auto",
            "outlook_mode": "owa",
            "owa_base_url": "https://correo.entelcc.cl/owa",
        }

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM app_settings;")
                for row in cursor.fetchall():
                    key = row["key"]
                    val = row["value"]
                    if key in defaults:
                        defaults[key] = val or ""
            # Si venía como 'web' genérico previo, mapearlo a 'owa'
            if defaults.get("outlook_mode") == "web":
                defaults["outlook_mode"] = "owa"
        except Exception as e:
            logger.error(f"Error al leer configuración de destinatarios: {e}", exc_info=True)

        return defaults

    def save_recipients_settings(
        self,
        boss_email: str,
        boss_phone: str,
        supervisor_email: str = "",
        supervisor_phone: str = "",
        boss_name: str = "Jefe Directo",
        supervisor_name: str = "Encargado",
        preferred_browser: str = "auto",
        outlook_mode: str = "owa",
        owa_base_url: str = "https://correo.entelcc.cl/owa",
    ) -> bool:
        """
        Guarda o actualiza los datos de Jefe y Encargado en app_settings.
        """
        data = {
            "boss_name": boss_name.strip() or "Jefe Directo",
            "boss_email": boss_email.strip(),
            "boss_phone": boss_phone.strip(),
            "supervisor_name": supervisor_name.strip() or "Encargado",
            "supervisor_email": supervisor_email.strip(),
            "supervisor_phone": supervisor_phone.strip(),
            "preferred_browser": preferred_browser.strip() or "auto",
            "outlook_mode": outlook_mode.strip() or "owa",
            "owa_base_url": owa_base_url.strip() or "https://correo.entelcc.cl/owa",
        }

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for key, val in data.items():
                    cursor.execute("""
                        INSERT INTO app_settings (key, value, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(key) DO UPDATE SET
                            value = excluded.value,
                            updated_at = CURRENT_TIMESTAMP;
                    """, (key, val))
                conn.commit()
                logger.info("Configuración de destinatarios actualizada exitosamente.")
                return True
        except Exception as e:
            logger.error(f"Error al guardar configuración de destinatarios: {e}", exc_info=True)
            return False
