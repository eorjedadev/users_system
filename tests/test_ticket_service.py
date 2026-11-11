"""
Módulo de Pruebas: tests.test_ticket_service
Valida el registro, consulta por fecha y generación de reportes de tickets de atención.
"""

from datetime import date, datetime, timedelta
from pathlib import Path
import tempfile
import unittest

from app.models.database import DatabaseManager
from app.models.user import User
from app.services.ticket_service import TicketService


class TestTicketService(unittest.TestCase):
    """Pruebas unitarias de TicketService."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_tickets.db"
        self.db = DatabaseManager(self.db_path)
        self.service = TicketService(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_record_ticket_success(self):
        """Verifica que un ticket se registre correctamente con todos los datos."""
        user = User(
            id=10,
            full_name="Patricio Cortez",
            username="pcortez",
            rut="12345678-9",
            phone="225815431",
            email="patricio.cortez@security.cl",
            area_or_group="Banco Security",
        )
        ok, msg, ticket = self.service.record_ticket(
            ticket_number="INC-10928",
            user=user,
            issue_detail="Desbloqueo de cuenta tras verificación telefónica.",
        )
        self.assertTrue(ok)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.ticket_number, "INC-10928")
        self.assertEqual(ticket.user_full_name, "Patricio Cortez")
        self.assertEqual(ticket.username, "pcortez")
        self.assertEqual(ticket.phone, "225815431")
        self.assertIn("Desbloqueo", ticket.issue_detail)

    def test_record_ticket_validation_empty_number(self):
        """Rechaza tickets sin número de ticket."""
        ok, msg, ticket = self.service.record_ticket(
            ticket_number="   ",
            user=None,
            issue_detail="Algún problema",
        )
        self.assertFalse(ok)
        self.assertIn("número de ticket", msg)

    def test_get_tickets_for_date_and_formatting(self):
        """Verifica la consulta por fecha y el formateo de reportes de correo y WhatsApp."""
        today = date.today()
        user1 = User(id=1, full_name="Carlos Gomez", username="cgomez", area_or_group="TI")
        user2 = User(id=2, full_name="Andrea Morales", username="amorales", phone="99887766")

        self.service.record_ticket("INC-01", user1, "Problema con mouse y monitor.")
        self.service.record_ticket("INC-02", user2, "Configuración de credenciales VPN.")

        tickets = self.service.get_tickets_for_date(today)
        self.assertEqual(len(tickets), 2)

        # Formato Correo
        report_email = TicketService.format_daily_report_email(tickets, today)
        self.assertIn("REPORTE DIARIO DE ATENCIONES", report_email)
        self.assertIn("Ticket #1: INC-01", report_email)
        self.assertIn("Carlos Gomez", report_email)
        self.assertIn("Ticket #2: INC-02", report_email)
        self.assertIn("Andrea Morales", report_email)
        self.assertIn("Total tickets gestionados: 2", report_email)

        # Formato WhatsApp
        report_wa = TicketService.format_daily_report_whatsapp(tickets, today)
        self.assertIn("*REPORTE DIARIO DE ATENCIONES*", report_wa)
        self.assertIn("INC-01", report_wa)
        self.assertIn("Carlos Gomez", report_wa)
        self.assertIn("INC-02", report_wa)
        self.assertIn("2 ticket(s) completado(s)", report_wa)


if __name__ == "__main__":
    unittest.main()
