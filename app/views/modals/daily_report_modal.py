"""
MÓDULO REUTILIZABLE: app.views.modals.daily_report_modal

DESCRIPCIÓN:
    Diálogo modal para generar, previsualizar y despachar el reporte consolidado diario
    a través de Microsoft Outlook y WhatsApp Web/Desktop.
"""

from datetime import date, timedelta
from typing import List, Optional
import tkinter as tk
from tkinter import messagebox, ttk

from app.models.ticket import Ticket
from app.services.dispatch_service import DispatchService
from app.services.settings_service import SettingsService
from app.services.ticket_service import TicketService
from app.utils.window_utils import apply_app_icon


class DailyReportModal(tk.Toplevel):
    """Ventana modal de generación y envío de reportes diarios."""

    def __init__(
        self,
        parent: tk.Misc,
        ticket_service: TicketService,
        settings_service: SettingsService,
        on_open_settings_callback=None,
    ):
        super().__init__(parent)
        self.ticket_service = ticket_service
        self.settings_service = settings_service
        self.on_open_settings_callback = on_open_settings_callback

        self.title("Reporte Diario de Tickets — Envío a Jefatura")
        self.minsize(680, 560)
        self.resizable(True, True)
        self.configure(bg="#f8fafc")
        apply_app_icon(self)

        self.transient(parent)
        self.grab_set()

        # Fecha por defecto: Ayer
        self.selected_date = date.today() - timedelta(days=1)
        self.current_tickets: List[Ticket] = []

        self._build_ui()
        self._load_report_for_date(self.selected_date)
        self._center_window(parent)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # 1. Barra superior: Selector de Fecha (Ayer / Hoy) y Configuración
        top_bar = ttk.Frame(container)
        top_bar.pack(fill="x", pady=(0, 10))

        ttk.Label(top_bar, text="Período del Reporte:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))

        self.btn_yesterday = ttk.Button(
            top_bar,
            text="📅  Ayer",
            style="Primary.TButton",
            command=self._select_yesterday,
            cursor="hand2",
        )
        self.btn_yesterday.pack(side="left", padx=(0, 6))

        self.btn_today = ttk.Button(
            top_bar,
            text="📅  Hoy",
            style="Outline.TButton",
            command=self._select_today,
            cursor="hand2",
        )
        self.btn_today.pack(side="left", padx=(0, 12))

        self.lbl_date_info = ttk.Label(
            top_bar,
            text="",
            font=("Segoe UI", 9, "italic"),
            foreground="#475569",
        )
        self.lbl_date_info.pack(side="left")

        btn_cfg = ttk.Button(
            top_bar,
            text="⚙️  Destinatarios",
            style="Action.TButton",
            command=self._handle_open_settings,
            cursor="hand2",
        )
        btn_cfg.pack(side="right")

        # 2. Resumen rápido de contador
        self.lbl_count_summary = ttk.Label(
            container,
            text="Cargando tickets...",
            font=("Segoe UI", 9, "bold"),
            foreground="#0b2545",
        )
        self.lbl_count_summary.pack(anchor="w", pady=(0, 6))

        # 3. Vista previa del reporte (Text con Scrollbar)
        preview_frame = ttk.Frame(container)
        preview_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.text_preview = tk.Text(
            preview_frame,
            wrap="word",
            font=("Consolas", 9),
            bg="#ffffff",
            fg="#0f172a",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=10,
        )
        self.text_preview.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(preview_frame, orient="vertical", command=self.text_preview.yview)
        self.text_preview.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # 4. Barra de Acciones de Envío (Outlook, WhatsApp Jefe, WhatsApp Encargado, Copiar)
        action_bar = ttk.Frame(container)
        action_bar.pack(fill="x", pady=(4, 0))

        # Botón Outlook
        self.btn_outlook = ttk.Button(
            action_bar,
            text="📧  Abrir en Outlook",
            style="Outlook.TButton",
            command=self._send_via_outlook,
            cursor="hand2",
        )
        self.btn_outlook.pack(side="left", padx=(0, 8))

        # Botón WhatsApp Jefe (Verde WhatsApp sólido)
        self.btn_wa_boss = ttk.Button(
            action_bar,
            text="💬  WhatsApp Jefe",
            style="WhatsApp.TButton",
            command=self._send_wa_boss,
            cursor="hand2",
        )
        self.btn_wa_boss.pack(side="left", padx=(0, 8))

        # Botón WhatsApp Encargado (Verde pastel contorno)
        self.btn_wa_sup = ttk.Button(
            action_bar,
            text="💬  WhatsApp Encargado",
            style="WhatsAppOutline.TButton",
            command=self._send_wa_supervisor,
            cursor="hand2",
        )
        self.btn_wa_sup.pack(side="left", padx=(0, 8))

        # Botón Copiar al portapapeles
        self.btn_copy = ttk.Button(
            action_bar,
            text="📋  Copiar Reporte",
            style="Outline.TButton",
            command=self._copy_to_clipboard,
            cursor="hand2",
        )
        self.btn_copy.pack(side="left")

        # Botón Cerrar (derecha) con icono ✕
        btn_close = ttk.Button(
            action_bar,
            text="✕  Cerrar",
            style="Action.TButton",
            command=self.destroy,
            cursor="hand2",
        )
        btn_close.pack(side="right")

    def _select_yesterday(self) -> None:
        self.selected_date = date.today() - timedelta(days=1)
        self.btn_yesterday.configure(style="Primary.TButton")
        self.btn_today.configure(style="Outline.TButton")
        self._load_report_for_date(self.selected_date)

    def _select_today(self) -> None:
        self.selected_date = date.today()
        self.btn_today.configure(style="Primary.TButton")
        self.btn_yesterday.configure(style="Outline.TButton")
        self._load_report_for_date(self.selected_date)

    def _load_report_for_date(self, target_date: date) -> None:
        self.current_tickets = self.ticket_service.get_tickets_for_date(target_date)
        date_display = target_date.strftime("%d/%m/%Y")
        count = len(self.current_tickets)

        self.lbl_date_info.configure(text=f"Fecha: {date_display}")
        self.lbl_count_summary.configure(
            text=f"Total de atenciones encontradas: {count} ticket(s)",
            foreground="#0284c7" if count > 0 else "#64748b",
        )

        report_text = self.ticket_service.format_daily_report_email(self.current_tickets, target_date)
        self.text_preview.delete("1.0", tk.END)
        self.text_preview.insert("1.0", report_text)

    def _send_via_outlook(self) -> None:
        if not self.current_tickets:
            messagebox.showwarning(
                "Sin Tickets",
                f"No hay atenciones registradas para la fecha seleccionada ({self.selected_date.strftime('%d/%m/%Y')}).",
                parent=self,
            )
            return

        recipients = self.settings_service.get_recipients_settings()
        boss_email = recipients.get("boss_email", "").strip()
        sup_email = recipients.get("supervisor_email", "").strip()

        if not boss_email and not sup_email:
            ask = messagebox.askyesno(
                "Destinatarios no configurados",
                "Aún no has configurado los correos de tu Jefe o Encargado.\n\n"
                "¿Deseas abrir la ventana de configuración ahora?",
                parent=self,
            )
            if ask:
                self._handle_open_settings()
            return

        to_list = [boss_email] if boss_email else []
        cc_list = [sup_email] if sup_email else []

        date_str = self.selected_date.strftime("%d/%m/%Y")
        subject = f"Reporte Diario de Atenciones y Tickets - {date_str} ({len(self.current_tickets)} tickets)"
        body = self.ticket_service.format_daily_report_email(self.current_tickets, self.selected_date)

        # Copiar también al portapapeles por comodidad
        try:
            self.clipboard_clear()
            self.clipboard_append(body)
            self.update()
        except Exception:
            pass

        pref_browser = recipients.get("preferred_browser", "auto")
        outlook_mode = recipients.get("outlook_mode", "owa")
        owa_base_url = recipients.get("owa_base_url", "https://correo.entelcc.cl/owa")

        ok, msg = DispatchService.open_outlook_email(
            to_list,
            cc_list,
            subject,
            body,
            outlook_mode=outlook_mode,
            preferred_browser=pref_browser,
            owa_base_url=owa_base_url,
        )
        if ok:
            if outlook_mode in ("owa", "web"):
                channel_info = "en Correo Corporativo Entel (Opera)"
                extra_tip = (
                    "Los destinatarios (Para y CC) y el asunto ya están listos.\n\n"
                    "El reporte consolidado está copiado en tu portapapeles: "
                    "haz un clic en el mensaje y presiona Ctrl + V para pegarlo."
                )
            elif outlook_mode == "office365":
                channel_info = "en Outlook Web Office 365"
                extra_tip = "El texto del reporte también ha sido copiado a tu portapapeles por comodidad."
            else:
                channel_info = "en Microsoft Outlook de escritorio"
                extra_tip = "El texto del reporte también ha sido copiado a tu portapapeles por comodidad."

            messagebox.showinfo(
                "Correo Preparado",
                f"Se ha abierto la redacción {channel_info}.\n\n{extra_tip}",
                parent=self,
            )
        else:
            messagebox.showerror("Error al Abrir Correo", msg, parent=self)

    def _send_wa_boss(self) -> None:
        recipients = self.settings_service.get_recipients_settings()
        phone = recipients.get("boss_phone", "").strip()
        self._dispatch_whatsapp(phone, "Jefe Directo")

    def _send_wa_supervisor(self) -> None:
        recipients = self.settings_service.get_recipients_settings()
        phone = recipients.get("supervisor_phone", "").strip()
        self._dispatch_whatsapp(phone, "Encargado")

    def _dispatch_whatsapp(self, phone: str, contact_title: str) -> None:
        if not self.current_tickets:
            messagebox.showwarning(
                "Sin Tickets",
                f"No hay atenciones registradas para la fecha seleccionada ({self.selected_date.strftime('%d/%m/%Y')}).",
                parent=self,
            )
            return

        if not phone:
            ask = messagebox.askyesno(
                "Número no configurado",
                f"No has configurado el número de WhatsApp para '{contact_title}'.\n\n"
                "¿Deseas abrir la ventana de configuración ahora?",
                parent=self,
            )
            if ask:
                self._handle_open_settings()
            return

        msg_text = self.ticket_service.format_daily_report_whatsapp(self.current_tickets, self.selected_date)
        
        # Copiar simultáneamente al portapapeles
        try:
            self.clipboard_clear()
            self.clipboard_append(msg_text)
            self.update()
        except Exception:
            pass

        recipients = self.settings_service.get_recipients_settings()
        pref_browser = recipients.get("preferred_browser", "auto")

        ok, msg = DispatchService.open_whatsapp_chat(phone, msg_text, preferred_browser=pref_browser)
        if ok:
            messagebox.showinfo(
                "WhatsApp Abierto",
                f"Se abrió WhatsApp para {contact_title}.\n\n"
                "El texto del reporte también ha sido copiado a tu portapapeles por comodidad.",
                parent=self,
            )
        else:
            messagebox.showerror("Error WhatsApp", msg, parent=self)

    def _copy_to_clipboard(self) -> None:
        report_text = self.text_preview.get("1.0", tk.END).strip()
        if not report_text:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(report_text)
            self.update()
            messagebox.showinfo("Copiado", "Reporte consolidado copiado al portapapeles exitosamente.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar al portapapeles: {e}", parent=self)

    def _handle_open_settings(self) -> None:
        if self.on_open_settings_callback:
            self.on_open_settings_callback()

    def _center_window(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        w = 700
        h = 580
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
