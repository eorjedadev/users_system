"""
Módulo de Pruebas: tests.test_document_service
Valida la generación, formateo y exportación a TXT de documentos independientes.
"""

from pathlib import Path
import tempfile
import unittest

from app.models.user import User
from app.services.document_service import DocumentService


class TestDocumentService(unittest.TestCase):
    """Pruebas del módulo de documentos independientes."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_txt_file_utf8_and_line_breaks(self):
        """Verifica que el archivo TXT se guarde en UTF-8 con saltos de línea y caracteres especiales."""
        target_file = self.output_dir / "documento_test.txt"
        test_content = (
            "DOCUMENTO DE PRUEBA OFICIAL\n"
            "Observación: Usuario validó información con éxito.\n"
            "Caracteres especiales: á, é, í, ó, ú, ñ, Ñ, ¿?, ¡!.\n"
            "Fin del documento."
        )

        ok, msg = DocumentService.save_to_txt_file(target_file, test_content)
        self.assertTrue(ok)
        self.assertTrue(target_file.exists())

        # Leer archivo en binario para verificar saltos de línea \r\n
        with open(target_file, "rb") as f:
            raw_bytes = f.read()
            self.assertIn(b"\r\n", raw_bytes)

        # Leer archivo en texto UTF-8 para verificar caracteres intactos
        with open(target_file, "r", encoding="utf-8") as f:
            read_text = f.read()
            self.assertIn("á, é, í, ó, ú, ñ, Ñ", read_text)
            self.assertIn("DOCUMENTO DE PRUEBA OFICIAL", read_text)

    def test_combine_document_with_user_selected(self):
        """Verifica la fusión correcta de la ficha de usuario y el texto redactado."""
        user = User(
            id=42,
            full_name="Gonzalo Henríquez Silva",
            username="ghenriquez",
            rut="14567890-2",
            phone="229016111",
            email="gonzalo.h@security.cl",
            area_or_group="Riesgo Operacional",
            address="Apoquindo 3150, Piso 8",
        )
        editor_text = "Se autoriza el desbloqueo temporal del usuario tras verificación telefónica."

        combined = DocumentService.combine_document(user, editor_text, include_user=True)
        self.assertIn("Resumen del usuario", combined)
        self.assertIn("Nombre completo: Gonzalo Henríquez Silva", combined)
        self.assertIn("Usuario: ghenriquez", combined)
        self.assertIn("RUT: 14567890-2", combined)
        self.assertIn("Detalle del problema:", combined)
        self.assertIn(editor_text, combined)
        self.assertNotIn("DATOS DEL USUARIO", combined)
        self.assertNotIn("=", combined)

    def test_combine_document_without_user(self):
        """Si include_user es False, solo se conserva el texto del documento."""
        user = User(id=1, full_name="Pedro Pascal")
        editor_text = "Nota interna independiente."

        result = DocumentService.combine_document(user, editor_text, include_user=False)
        self.assertEqual(result, editor_text)
        self.assertNotIn("Resumen del usuario", result)

    def test_reject_empty_document(self):
        """Verifica que no se permita guardar archivos vacíos."""
        target_file = self.output_dir / "empty.txt"
        ok, msg = DocumentService.save_to_txt_file(target_file, "    ")
        self.assertFalse(ok)
        self.assertFalse(target_file.exists())


if __name__ == "__main__":
    unittest.main()
