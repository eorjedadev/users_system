"""
PROYECTO: Sistema de Gestión de Usuarios, Documentación y Despacho Operativo
AUTOR: Eduardo Orjeda Figueroa | Lead Software Engineer & Prompt Engineer
METODOLOGÍA: AI-Augmented Software Engineering vía Google Gemini
MÓDULO: app.services.dispatch_service

DESCRIPCIÓN:
    Servicio de integración universal con Microsoft Outlook (Web Office 365 y Escritorio)
    y WhatsApp Web/Desktop en Windows para el envío automático de reportes de atenciones.

RESPONSABILIDAD:
    - Detectar el navegador en uso activo (Opera, Chrome, Edge) o respetar la preferencia configurada.
    - Abrir WhatsApp Web directamente en el navegador del usuario preservando sesiones activas.
    - Abrir Outlook Web (Office 365 Deeplink Compose) o Microsoft Outlook Desktop según la configuración.
    - Respaldar el contenido en el portapapeles del sistema operativo para máxima confiabilidad.
"""

from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple
import urllib.parse
import webbrowser

from app.utils.logger import get_logger

logger = get_logger("dispatch_service")


class DispatchService:
    """Servicio de despacho de reportes por canales corporativos y web."""

    @classmethod
    def clean_phone_number(cls, phone_raw: str) -> str:
        """Limpia el teléfono dejando únicamente dígitos numéricos internacionales."""
        digits = re.sub(r"[^\d]", "", phone_raw)
        return digits

    @staticmethod
    def get_browser_executable(browser_key: str) -> Optional[Path]:
        """
        Retorna la ruta al ejecutable del navegador especificado ('opera', 'chrome', 'edge').
        """
        home = Path.home()
        key = browser_key.lower().strip()
        candidates = []

        if key == "opera":
            candidates = [
                home / "AppData/Local/Programs/Opera/opera.exe",
                home / "AppData/Local/Programs/Opera/launcher.exe",
                Path("C:/Program Files/Opera/opera.exe"),
                Path("C:/Program Files/Opera/launcher.exe"),
                Path("C:/Program Files (x86)/Opera/opera.exe"),
                Path("C:/Program Files (x86)/Opera/launcher.exe"),
            ]
        elif key == "chrome":
            candidates = [
                Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
                Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
                home / "AppData/Local/Google/Chrome/Application/chrome.exe",
            ]
        elif key == "edge":
            candidates = [
                Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
                Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
            ]

        for p in candidates:
            if p.exists():
                return p

        # Fallback a PATH con shutil.which
        which_cmd = "msedge" if key == "edge" else key
        which_path = shutil.which(which_cmd)
        if which_path:
            return Path(which_path)

        return None

    @classmethod
    def is_process_running(cls, process_name: str) -> bool:
        """Comprueba si un proceso de navegador está en ejecución en Windows."""
        try:
            r = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return process_name.lower() in r.stdout.lower()
        except Exception:
            return False

    @classmethod
    def detect_active_browser(cls) -> str:
        """
        Detecta qué navegador está en ejecución activa en el sistema.
        Prioriza Opera si está abierto, luego Chrome, luego Edge.
        """
        if cls.is_process_running("opera.exe"):
            return "opera"
        if cls.is_process_running("chrome.exe"):
            return "chrome"
        if cls.is_process_running("msedge.exe"):
            return "edge"
        return "default"

    @classmethod
    def open_url_in_browser(cls, url: str, preferred_browser: str = "auto") -> Tuple[bool, str]:
        """
        Abre una URL en el navegador indicado o detectado automáticamente.
        """
        browser_choice = (preferred_browser or "auto").lower().strip()
        if browser_choice == "auto":
            browser_choice = cls.detect_active_browser()

        if browser_choice in ("opera", "chrome", "edge"):
            exe_path = cls.get_browser_executable(browser_choice)
            if exe_path and exe_path.exists():
                try:
                    subprocess.Popen([str(exe_path), url], shell=False)
                    logger.info(f"URL abierta exitosamente en {browser_choice.capitalize()} ({exe_path})")
                    return (True, f"Enlace abierto en {browser_choice.capitalize()}.")
                except Exception as e:
                    logger.warning(f"Error al invocar ejecutable de {browser_choice}: {e}. Usando fallback...")

        # Fallback al navegador estándar del sistema
        try:
            webbrowser.open(url)
            logger.info("URL abierta con navegador estándar de Windows.")
            return (True, "Enlace abierto en el navegador.")
        except Exception as e:
            logger.error(f"Error al abrir URL en navegador: {e}", exc_info=True)
            return (False, f"No se pudo abrir el navegador: {e}")

    @classmethod
    def open_outlook_email(
        cls,
        to_emails: List[str],
        cc_emails: Optional[List[str]] = None,
        subject: str = "",
        body: str = "",
        outlook_mode: str = "owa",
        preferred_browser: str = "auto",
        owa_base_url: str = "https://correo.entelcc.cl/owa",
    ) -> Tuple[bool, str]:
        """
        Abre Microsoft Outlook en la modalidad configurada:
        - 'owa': Redacta mediante el servidor corporativo Exchange OWA (correo.entelcc.cl) en el navegador activo (Opera).
        - 'office365': Redacta mediante Office 365 Web Deeplink en el navegador activo (Opera/Chrome/Edge).
        - 'desktop': Invoca la aplicación de escritorio de Outlook mediante automatización COM.
        """
        to_str = ", ".join([e.strip() for e in to_emails if e and e.strip()])
        cc_str = ", ".join([e.strip() for e in (cc_emails or []) if e and e.strip()])

        if not to_str and not cc_str:
            return (False, "Debe especificar al menos un correo de destinatario (Jefe o Encargado).")

        mode = (outlook_mode or "owa").lower().strip()

        # 1. Modo OWA Corporativo (correo.entelcc.cl)
        # OWA on-premise (IIS) rechaza URLs largas si se incluye un cuerpo extenso por query string (error HTTP 500 / Algo no fue bien).
        # Por tanto, enviamos 'to', 'cc' y 'subject' en la URL (URL limpia y ligera), y el cuerpo se entrega en el portapapeles.
        if mode in ("owa", "web"):
            base = (owa_base_url or "https://correo.entelcc.cl/owa").rstrip("/")
            if not base.endswith("/owa"):
                base = f"{base}/owa"

            params = {}
            if to_str:
                params["to"] = to_str
            if cc_str:
                params["cc"] = cc_str
            if subject:
                params["subject"] = subject

            query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            owa_url = f"{base}/?path=/mail/action/compose&{query}"
            return cls.open_url_in_browser(owa_url, preferred_browser=preferred_browser)

        # 2. Modo Office 365 Deeplink Compose
        if mode == "office365":
            params = {}
            if to_str:
                params["to"] = to_str
            if cc_str:
                params["cc"] = cc_str
            if subject:
                params["subject"] = subject
            if body:
                params["body"] = body

            query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            web_url = f"https://outlook.office.com/mail/deeplink/compose?{query}"
            return cls.open_url_in_browser(web_url, preferred_browser=preferred_browser)

        # 2. Modo Escritorio (App Windows)
        if sys.platform.startswith("win"):
            try:
                ps_to = "; ".join([e.strip() for e in to_emails if e and e.strip()])
                ps_cc = "; ".join([e.strip() for e in (cc_emails or []) if e and e.strip()])
                ps_script = f"""
                $ErrorActionPreference = 'Stop'
                try {{
                    $outlook = New-Object -ComObject Outlook.Application
                    $mail = $outlook.CreateItem(0)
                    $mail.To = {cls._ps_quote(ps_to)}
                    $mail.CC = {cls._ps_quote(ps_cc)}
                    $mail.Subject = {cls._ps_quote(subject)}
                    $mail.Body = {cls._ps_quote(body)}
                    $mail.Display()
                }} catch {{
                    exit 1
                }}
                """
                proc = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if proc.returncode == 0:
                    logger.info("Ventana de Outlook de escritorio abierta exitosamente mediante automatización COM.")
                    return (True, "Mensaje abierto exitosamente en Microsoft Outlook de escritorio.")
            except Exception as e:
                logger.warning(f"No se pudo invocar Outlook COM ({e}). Usando fallback mailto...")

        # Fallback estándar mediante protocolo mailto
        try:
            params = {}
            if cc_str:
                params["cc"] = cc_str
            if subject:
                params["subject"] = subject
            if body:
                params["body"] = body[:1800] if len(body) > 1800 else body

            query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            mailto_url = f"mailto:{to_str}?{query}" if to_str else f"mailto:?{query}"
            cls.open_url_in_browser(mailto_url, preferred_browser=preferred_browser)
            logger.info("Enlace mailto ejecutado con éxito.")
            return (True, "Cliente de correo abierto exitosamente.")
        except Exception as e:
            logger.error(f"Error al abrir cliente de correo: {e}", exc_info=True)
            return (False, f"No se pudo abrir el cliente de correo: {e}")

    @classmethod
    def open_whatsapp_chat(
        cls,
        phone_raw: str,
        message_text: str,
        preferred_browser: str = "auto",
    ) -> Tuple[bool, str]:
        """
        Abre WhatsApp Web en el navegador seleccionado (Opera, Chrome, Edge, etc.)
        con el mensaje y el número fijados.
        """
        clean_phone = cls.clean_phone_number(phone_raw)
        encoded_text = urllib.parse.quote(message_text)

        if clean_phone:
            url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
        else:
            url = f"https://web.whatsapp.com/send?text={encoded_text}"

        return cls.open_url_in_browser(url, preferred_browser=preferred_browser)

    @staticmethod
    def _ps_quote(val: str) -> str:
        """Escapa cadenas de texto para inclusión segura en argumentos PowerShell."""
        escaped = val.replace("`", "``").replace('"', '`"').replace("$", "`$")
        return f'"{escaped}"'
