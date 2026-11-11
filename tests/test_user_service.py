"""
Módulo de Pruebas: tests.test_user_service
Valida el servicio de usuarios, validaciones y operaciones CRUD.
"""

from pathlib import Path
import tempfile
import unittest

from app.models.database import DatabaseManager
from app.services.user_service import UserService
from app.services.validation_service import ValidationService


class TestUserService(unittest.TestCase):
    """Pruebas funcionales de operaciones de usuario y validaciones."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_users_crud.db"
        self.db = DatabaseManager(self.db_path)
        self.service = UserService(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_valid_user(self):
        """Verifica la creación exitosa de un usuario válido."""
        user_data = {
            "full_name": "Ana Morales Perez",
            "username": "amorales",
            "rut": "15123456-k",
            "phone": "987654321",
            "email": "ana.morales@security.cl",
            "area_or_group": "Operaciones",
            "address": "Agustinas 1234",
        }
        success, user, msg = self.service.create_user(user_data)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.full_name, "Ana Morales Perez")
        self.assertEqual(user.rut, "15123456-K")  # Normalizado a mayúscula

    def test_validation_rejects_empty_or_short_name(self):
        """Rechaza nombres vacíos o menores a 3 caracteres."""
        # Nombre vacío
        ok, user, msg = self.service.create_user({"full_name": ""})
        self.assertFalse(ok)
        self.assertIn("obligatorio", msg.lower())

        # Nombre de 2 caracteres
        ok, user, msg = self.service.create_user({"full_name": "Al"})
        self.assertFalse(ok)
        self.assertIn("3 caracteres", msg.lower())

    def test_validation_email_and_phone(self):
        """Verifica validación de sintaxis de correo y teléfono."""
        # Correo sin arroba o sin dominio
        ok, user, msg = self.service.create_user({"full_name": "Carlos Gomez", "email": "carlos.sin_arroba"})
        self.assertFalse(ok)
        self.assertIn("correo", msg.lower())

        # Teléfono con caracteres inválidos
        ok, user, msg = self.service.create_user({"full_name": "Carlos Gomez", "phone": "abc???999"})
        self.assertFalse(ok)
        self.assertIn("teléfono", msg.lower())

    def test_search_users_multi_field(self):
        """Verifica que la búsqueda encuentre coincidencias en Nombre, Usuario, RUT o Teléfono."""
        self.service.create_user({"full_name": "Jorge Valenzuela", "username": "jvalenzuela", "rut": "12345678-5", "phone": "229016000"})
        self.service.create_user({"full_name": "Patricia Reyes", "username": "preyes", "rut": "18765432-1", "phone": "225815000"})
        self.service.create_user({"full_name": "Rodrigo Silva", "username": "rsilva", "rut": "20111222-3", "phone": "987654321"})

        # Búsqueda por parte de nombre (case-insensitive)
        res_name = self.service.search_users("valenzuela")
        self.assertEqual(len(res_name), 1)
        self.assertEqual(res_name[0].full_name, "Jorge Valenzuela")

        # Búsqueda por parte de usuario
        res_user = self.service.search_users("preyes")
        self.assertEqual(len(res_user), 1)
        self.assertEqual(res_user[0].full_name, "Patricia Reyes")

        # Búsqueda por parte de RUT
        res_rut = self.service.search_users("20111222")
        self.assertEqual(len(res_rut), 1)
        self.assertEqual(res_rut[0].full_name, "Rodrigo Silva")

        # Búsqueda por teléfono
        res_phone = self.service.search_users("225815000")
        self.assertEqual(len(res_phone), 1)
        self.assertEqual(res_phone[0].full_name, "Patricia Reyes")

    def test_update_user(self):
        """Verifica la modificación de un usuario preservando su ID interno."""
        ok, user, _ = self.service.create_user({"full_name": "Original Name", "phone": "111111"})
        self.assertTrue(ok)
        original_id = user.id

        update_data = {
            "id": original_id,
            "full_name": "Modified Name",
            "phone": "999999",
            "email": "mod@security.cl",
        }
        ok_up, updated, msg = self.service.update_user(update_data)
        self.assertTrue(ok_up)
        self.assertEqual(updated.id, original_id)
        self.assertEqual(updated.full_name, "Modified Name")
        self.assertEqual(updated.phone, "999999")
        self.assertEqual(updated.email, "mod@security.cl")

    def test_delete_user(self):
        """Verifica la eliminación definitiva de un registro."""
        ok, user, _ = self.service.create_user({"full_name": "User To Delete"})
        self.assertEqual(self.service.get_total_count(), 1)

        ok_del, msg = self.service.delete_user(user.id)
        self.assertTrue(ok_del)
        self.assertEqual(self.service.get_total_count(), 0)
        self.assertIsNone(self.service.get_user_by_id(user.id))


if __name__ == "__main__":
    unittest.main()
