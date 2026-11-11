"""
Módulo de Pruebas: tests.test_dispatch_service
Valida los métodos de despacho universal para WhatsApp Web y Microsoft Outlook (Web y Escritorio).
"""

from unittest.mock import patch, MagicMock
import unittest

from app.services.dispatch_service import DispatchService


class TestDispatchService(unittest.TestCase):
    """Pruebas unitarias de DispatchService."""

    def test_clean_phone_number(self):
        """Limpia formatos de teléfono a sólo dígitos."""
        self.assertEqual(DispatchService.clean_phone_number("+56 9 6692 0578"), "56966920578")
        self.assertEqual(DispatchService.clean_phone_number("  +56-9-1234-5678  "), "56912345678")
        self.assertEqual(DispatchService.clean_phone_number(""), "")

    def test_open_outlook_email_validation(self):
        """Rechaza apertura sin destinatarios."""
        ok, msg = DispatchService.open_outlook_email([], [])
        self.assertFalse(ok)
        self.assertIn("Debe especificar al menos un correo", msg)

    @patch("app.services.dispatch_service.DispatchService.open_url_in_browser")
    def test_open_outlook_email_corporate_owa(self, mock_open_url):
        """Verifica que el modo 'owa' genere la URL para el servidor Exchange corporativo."""
        mock_open_url.return_value = (True, "Enlace abierto.")

        ok, msg = DispatchService.open_outlook_email(
            to_emails=["jefe@empresa.com"],
            cc_emails=["encargado@empresa.com"],
            subject="Reporte Diario",
            body="Detalle de tickets...",
            outlook_mode="owa",
            preferred_browser="opera",
            owa_base_url="https://correo.entelcc.cl/owa",
        )
        self.assertTrue(ok)
        mock_open_url.assert_called_once()
        called_url = mock_open_url.call_args[0][0]
        self.assertTrue(called_url.startswith("https://correo.entelcc.cl/owa/?path=/mail/action/compose&"))
        self.assertIn("to=jefe%40empresa.com", called_url)
        self.assertIn("cc=encargado%40empresa.com", called_url)
        self.assertNotIn("body=", called_url)
        self.assertEqual(mock_open_url.call_args[1].get("preferred_browser"), "opera")

    @patch("app.services.dispatch_service.DispatchService.open_url_in_browser")
    def test_open_outlook_email_office365(self, mock_open_url):
        """Verifica que el modo 'office365' genere la URL oficial de Office 365 Deeplink Compose."""
        mock_open_url.return_value = (True, "Enlace abierto.")

        ok, msg = DispatchService.open_outlook_email(
            to_emails=["jefe@empresa.com"],
            cc_emails=["encargado@empresa.com"],
            subject="Reporte Diario",
            body="Detalle de tickets...",
            outlook_mode="office365",
            preferred_browser="chrome",
        )
        self.assertTrue(ok)
        mock_open_url.assert_called_once()
        called_url = mock_open_url.call_args[0][0]
        self.assertTrue(called_url.startswith("https://outlook.office.com/mail/deeplink/compose?"))
        self.assertIn("to=jefe%40empresa.com", called_url)
        self.assertEqual(mock_open_url.call_args[1].get("preferred_browser"), "chrome")

    @patch("app.services.dispatch_service.DispatchService.open_url_in_browser")
    def test_open_whatsapp_chat_url(self, mock_open_url):
        """Verifica que se construya la URL de WhatsApp Web con el teléfono limpio y mensaje codificado."""
        mock_open_url.return_value = (True, "Enlace abierto en Opera.")

        ok, msg = DispatchService.open_whatsapp_chat(
            phone_raw="+56 9 6692 0578",
            message_text="Reporte de Ayer:\nTicket #1",
            preferred_browser="opera",
        )
        self.assertTrue(ok)
        mock_open_url.assert_called_once()
        called_url = mock_open_url.call_args[0][0]
        self.assertTrue(called_url.startswith("https://web.whatsapp.com/send?phone=56966920578"))
        self.assertIn("text=Reporte%20de%20Ayer", called_url)
        self.assertEqual(mock_open_url.call_args[1].get("preferred_browser"), "opera")


if __name__ == "__main__":
    unittest.main()
