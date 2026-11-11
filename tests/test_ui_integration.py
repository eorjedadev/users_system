from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.database import DatabaseManager
from app.services.user_service import UserService
from app.views.main_window import MainWindow
from app.controllers.user_controller import UserController
from app.controllers.document_controller import DocumentController


class TestUIIntegration(unittest.TestCase):
    """Pruebas de integración visual de la interfaz de 3 columnas."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test_ui.db"
        self.db = DatabaseManager(db_path=db_path)
        self.user_service = UserService(self.db)

        # Crear usuarios de prueba
        self.user_service.create_user({
            "full_name": "Carlos Gomez Silva",
            "username": "cgomez",
            "rut": "12.345.678-9",
            "phone": "+56912345678",
            "email": "carlos.gomez@empresa.com",
            "area_or_group": "Operaciones",
            "address": "Av. Libertador 1234",
        })

        self.window = MainWindow()
        self.window.withdraw()  # No mostrar ventana gráfica durante pruebas
        self.user_controller = UserController(self.window, self.user_service)
        self.doc_controller = DocumentController(self.window, self.user_controller)

    def tearDown(self):
        self.window.destroy()
        self.temp_dir.cleanup()

    def test_initial_ui_state(self):
        """Verifica que los botones de editar/eliminar comiencen deshabilitados y la ficha vacía."""
        self.assertIsNone(self.user_controller.get_current_user())
        self.assertEqual(str(self.window.actions_view.btn_edit["state"]), "disabled")
        self.assertEqual(str(self.window.actions_view.btn_delete["state"]), "disabled")
        self.assertEqual(str(self.window.user_card_view.btn_clear_sel["state"]), "disabled")
        self.assertIn("Selección ID: —", self.window.status_bar_view.lbl_info.cget("text"))

    def test_search_and_select_user(self):
        """Verifica que al buscar y seleccionar un usuario, la ficha y los botones se activen."""
        self.user_controller.search("Carlos")
        users = self.user_service.search_users("Carlos")
        self.assertEqual(len(users), 1)

        user_id = users[0].id
        self.user_controller.select_user(user_id)

        # Ficha poblada
        self.assertEqual(self.window.user_card_view.var_name.get(), "Carlos Gomez Silva")
        self.assertEqual(self.window.user_card_view.var_rut.get(), "12.345.678-9")
        self.assertEqual(self.window.user_card_view.var_email.get(), "carlos.gomez@empresa.com")
        self.assertEqual(self.window.user_card_view.var_area.get(), "Operaciones")
        self.assertEqual(self.window.user_card_view.var_address.get(), "Av. Libertador 1234")

        # Botones activados
        self.assertEqual(str(self.window.actions_view.btn_edit["state"]), "normal")
        self.assertEqual(str(self.window.actions_view.btn_delete["state"]), "normal")
        self.assertEqual(str(self.window.user_card_view.btn_clear_sel["state"]), "normal")

        # Barra de estado
        self.assertIn(f"Selección ID: #{user_id}", self.window.status_bar_view.lbl_info.cget("text"))

    def test_clear_selection(self):
        """Verifica que limpiar la selección resetee la ficha y los estados."""
        users = self.user_service.search_users("Carlos")
        self.user_controller.select_user(users[0].id)
        self.user_controller.clear_selection()

        self.assertIsNone(self.user_controller.get_current_user())
        self.assertEqual(self.window.user_card_view.var_name.get(), "")
        self.assertEqual(str(self.window.actions_view.btn_edit["state"]), "disabled")
        self.assertEqual(str(self.window.actions_view.btn_delete["state"]), "disabled")
        self.assertIn("Selección ID: —", self.window.status_bar_view.lbl_info.cget("text"))

    def test_document_editor_operations(self):
        """Verifica el funcionamiento del editor de documentos y placeholder."""
        # Inicialmente vacío (placeholder activo)
        self.assertEqual(self.window.document_view.get_document_text(), "")

        # Escribir contenido
        self.window.document_view.set_document_text("Reporte de incidencia en el servidor.")
        self.assertEqual(self.window.document_view.get_document_text(), "Reporte de incidencia en el servidor.")

        # Limpiar documento
        self.window.document_view.clear_document()
        self.assertEqual(self.window.document_view.get_document_text(), "")

    def test_multi_username_selection(self):
        """Verifica que un usuario con múltiples cuentas permita seleccionar con cuál trabajar."""
        self.user_service.create_user({
            "full_name": "Patricio Cortez",
            "usernames": "pcortez, adm_pcortez, sec_pcortez",
            "rut": "11.222.333-4",
            "email": "patricio.cortez@security.cl",
        })
        self.user_controller.search("Patricio")
        user = self.user_controller.get_current_user()
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, "Patricio Cortez")
        self.assertEqual(len(user.usernames), 3)
        self.assertIn("adm_pcortez", self.window.user_card_view.combo_user["values"])

        # Cambiar de cuenta seleccionada a adm_pcortez
        self.window.user_card_view.combo_user.set("adm_pcortez")
        self.window.user_card_view._on_combo_select()
        self.assertEqual(user.get_active_username(), "adm_pcortez")

    def test_record_ticket_ui_flow(self):
        """Verifica que el flujo de registro de ticket desde la interfaz guarde correctamente en la base de datos."""
        from unittest.mock import patch
        from app.services.ticket_service import TicketService

        ticket_service = TicketService(self.db)
        self.doc_controller.ticket_service = ticket_service

        # Seleccionar usuario
        self.user_controller.search("Carlos")
        self.assertIsNotNone(self.user_controller.get_current_user())

        # Configurar ticket y detalle
        self.window.document_view.set_ticket_number("INC-88991")
        self.window.document_view.set_document_text("Usuario solicita reseteo de clave.")

        # Ejecutar registro interceptando popups
        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.doc_controller.record_ticket()
            self.assertTrue(mock_info.called)

        # Verificar que el ticket quedó en la base de datos
        from datetime import date
        tickets = ticket_service.get_tickets_for_date(date.today())
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].ticket_number, "INC-88991")
        self.assertEqual(tickets[0].user_full_name, "Carlos Gomez Silva")

        # Verificar que los campos se limpiaron para la siguiente atención
        self.assertEqual(self.window.document_view.get_ticket_number(), "")
        self.assertEqual(self.window.document_view.get_document_text(), "")


if __name__ == "__main__":
    unittest.main()

