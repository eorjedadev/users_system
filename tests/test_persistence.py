"""
Módulo de Pruebas: tests.test_persistence
Valida el ciclo de vida, persistencia y estabilidad de la base de datos SQLite.
"""

import os
from pathlib import Path
import tempfile
import unittest

from app.models.database import DatabaseManager
from app.models.user import User


class TestDatabasePersistence(unittest.TestCase):
    """Pruebas de persistencia e integridad para SQLite."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_usuarios.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_first_run_creates_schema_and_indexes(self):
        """Verifica que en la primera ejecución se crea el archivo, tablas e índices."""
        self.assertFalse(self.db_path.exists())
        
        db = DatabaseManager(self.db_path)
        self.assertTrue(self.db_path.exists())
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Verificar existencia de la tabla users
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            self.assertIsNotNone(cursor.fetchone())
            
            # Verificar versión de esquema
            cursor.execute("PRAGMA user_version;")
            version = cursor.fetchone()[0]
            self.assertEqual(version, 1)

            # Verificar índices
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_users_%';")
            indexes = [row[0] for row in cursor.fetchall()]
            self.assertIn("idx_users_full_name", indexes)
            self.assertIn("idx_users_username", indexes)
            self.assertIn("idx_users_rut", indexes)
            self.assertIn("idx_users_phone", indexes)

    def test_persistence_between_sessions(self):
        """Verifica que los datos persisten al cerrar y reabrir la base de datos."""
        # 1. Sesión 1: Crear e insertar registro
        db1 = DatabaseManager(self.db_path)
        with db1.get_connection() as conn:
            conn.execute(
                "INSERT INTO users (full_name, username, rut, email) VALUES (?, ?, ?, ?);",
                ("Usuario Persistente", "upersist", "11222333-4", "pers@security.cl"),
            )
        self.assertEqual(db1.get_user_count(), 1)
        del db1  # Simular cierre de sesión

        # 2. Sesión 2: Reabrir el archivo existente
        db2 = DatabaseManager(self.db_path)
        self.assertEqual(db2.get_user_count(), 1)
        
        with db2.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, username, rut, email FROM users WHERE id = 1;")
            row = cursor.fetchone()
            self.assertEqual(row["full_name"], "Usuario Persistente")
            self.assertEqual(row["username"], "upersist")
            self.assertEqual(row["rut"], "11222333-4")
            self.assertEqual(row["email"], "pers@security.cl")

    def test_reopen_does_not_duplicate_or_truncate_data(self):
        """Comprueba que reabrir múltiples veces no duplica ni borra la información."""
        db = DatabaseManager(self.db_path)
        with db.get_connection() as conn:
            conn.execute("INSERT INTO users (full_name) VALUES ('Test 1');")
            conn.execute("INSERT INTO users (full_name) VALUES ('Test 2');")
        del db

        # Reabrir 3 veces consecutivas
        for _ in range(3):
            reopened_db = DatabaseManager(self.db_path)
            self.assertEqual(reopened_db.get_user_count(), 2)
            del reopened_db


if __name__ == "__main__":
    unittest.main()
