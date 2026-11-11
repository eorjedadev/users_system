"""
Módulo de Pruebas: tests.test_csv_service
Valida la inspección, detección de codificación, backup previo e importación masiva desde CSV.
"""

from pathlib import Path
import tempfile
import unittest

from app.models.database import DatabaseManager
from app.services.csv_service import CsvService


class TestCsvService(unittest.TestCase):
    """Pruebas de procesamiento y carga masiva de archivos CSV."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_csv_import.db"
        self.db = DatabaseManager(self.db_path)
        self.service = CsvService(self.db)
        project_root = Path(__file__).resolve().parent.parent
        csv_candidates = [
            project_root / "docs" / "data-1792514617949.csv",
            project_root / "data-1792514617949.csv",
        ]
        self.real_csv_path = next((p for p in csv_candidates if p.exists()), csv_candidates[0])

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_inspect_real_csv_file(self):
        """Verifica la inspección sin errores del archivo CSV real de 1.649 registros."""
        self.assertTrue(self.real_csv_path.exists())
        
        inspection = self.service.inspect_csv(self.real_csv_path)
        self.assertEqual(inspection.encoding.lower(), "utf-8")
        self.assertEqual(inspection.delimiter, ",")
        self.assertEqual(inspection.total_rows, 1649)
        self.assertIn("full_name", inspection.proposed_mapping)
        self.assertIn("username", inspection.proposed_mapping)
        self.assertIn("rut", inspection.proposed_mapping)

    def test_import_real_csv_data(self):
        """Ejecuta la importación masiva y comprueba persistencia e integridad."""
        initial_mtime = self.real_csv_path.stat().st_mtime
        
        # Ejecutar importación
        summary = self.service.import_csv_data(self.real_csv_path)
        
        # 1. Verificar que el CSV original NO fue alterado
        final_mtime = self.real_csv_path.stat().st_mtime
        self.assertEqual(initial_mtime, final_mtime, "El archivo CSV original no debe ser modificado.")

        # 2. Verificar que se creó copia de seguridad previa
        self.assertIsNotNone(summary.backup_path)
        self.assertTrue(summary.backup_path.exists())

        # 3. Comprobar registros insertados
        self.assertEqual(summary.total_read, 1649)
        self.assertEqual(summary.imported_count, 1649)
        self.assertEqual(self.db.get_user_count(), 1649)

        # 4. Verificar integridad de datos (RUT con K, teléfonos, etc.)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Verificar primer registro: Janny Andrea Toledo Santander
            cursor.execute("SELECT * FROM users WHERE full_name LIKE 'Janny Andrea%' LIMIT 1;")
            user_1 = cursor.fetchone()
            self.assertIsNotNone(user_1)
            self.assertEqual(user_1["username"], "jatoledo")
            self.assertEqual(user_1["rut"], "18311526-K")
            self.assertEqual(user_1["phone"], "225815678")


if __name__ == "__main__":
    unittest.main()
