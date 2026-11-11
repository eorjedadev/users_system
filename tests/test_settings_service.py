"""
Módulo de Pruebas: tests.test_settings_service
Valida la persistencia y lectura de los contactos de destinatarios (Jefe y Encargado).
"""

from pathlib import Path
import tempfile
import unittest

from app.models.database import DatabaseManager
from app.services.settings_service import SettingsService


class TestSettingsService(unittest.TestCase):
    """Pruebas unitarias de SettingsService."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_settings.db"
        self.db = DatabaseManager(self.db_path)
        self.service = SettingsService(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_settings(self):
        """Verifica que retorne valores por defecto limpios si no se ha configurado nada."""
        settings = self.service.get_recipients_settings()
        self.assertEqual(settings["boss_email"], "")
        self.assertEqual(settings["boss_phone"], "")
        self.assertEqual(settings["supervisor_email"], "")
        self.assertEqual(settings["supervisor_phone"], "")
        self.assertEqual(settings["preferred_browser"], "auto")
        self.assertEqual(settings["outlook_mode"], "owa")
        self.assertEqual(settings["owa_base_url"], "https://correo.entelcc.cl/owa")

    def test_save_and_retrieve_settings(self):
        """Guarda contactos de Jefe y Encargado y los recupera con exactitud."""
        ok = self.service.save_recipients_settings(
            boss_email="jefe@bancosecurity.cl",
            boss_phone="+56 9 1234 5678",
            supervisor_email="encargado@bancosecurity.cl",
            supervisor_phone="+56 9 8765 4321",
            boss_name="Rodrigo Jefe",
            supervisor_name="Maria Encargada",
            preferred_browser="opera",
            outlook_mode="owa",
            owa_base_url="https://correo.entelcc.cl/owa",
        )
        self.assertTrue(ok)

        settings = self.service.get_recipients_settings()
        self.assertEqual(settings["boss_email"], "jefe@bancosecurity.cl")
        self.assertEqual(settings["boss_phone"], "+56 9 1234 5678")
        self.assertEqual(settings["supervisor_email"], "encargado@bancosecurity.cl")
        self.assertEqual(settings["supervisor_phone"], "+56 9 8765 4321")
        self.assertEqual(settings["boss_name"], "Rodrigo Jefe")
        self.assertEqual(settings["supervisor_name"], "Maria Encargada")
        self.assertEqual(settings["preferred_browser"], "opera")
        self.assertEqual(settings["outlook_mode"], "owa")
        self.assertEqual(settings["owa_base_url"], "https://correo.entelcc.cl/owa")


if __name__ == "__main__":
    unittest.main()
