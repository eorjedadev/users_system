"""
MÓDULO REUTILIZABLE: app.views.modals.settings_modal

DESCRIPCIÓN:
    Diálogo modal para configurar los datos de contacto de Jefe y Encargado
    (correos y números de WhatsApp) almacenados de forma local y privada.
"""

from typing import Callable, Dict, Optional
import tkinter as tk
from tkinter import messagebox, ttk

from app.services.settings_service import SettingsService
from app.utils.window_utils import apply_app_icon
from config.settings import APP_AI_TOOL, APP_AUTHOR, APP_VERSION


class SettingsModal(tk.Toplevel):
    """Diálogo modal para configurar correos y teléfonos de destinatarios."""

    def __init__(
        self,
        parent: tk.Misc,
        settings_service: SettingsService,
        on_save_callback: Optional[Callable[[Dict[str, str]], None]] = None,
    ):
        super().__init__(parent)
        self.settings_service = settings_service
        self.on_save_callback = on_save_callback

        self.title("Configuración de Destinatarios (Jefe y Encargado)")
        self.minsize(500, 420)
        self.resizable(False, False)
        self.configure(bg="#f8fafc")
        apply_app_icon(self)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._load_current_data()
        self._center_window(parent)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        # 1. Sección Jefe Directo
        boss_frame = ttk.LabelFrame(container, text="  👤 Datos de Jefatura Directa  ", padding=12)
        boss_frame.pack(fill="x", pady=(0, 14))

        ttk.Label(boss_frame, text="Nombre o Cargo:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self.var_boss_name = tk.StringVar(value="Jefe Directo")
        ttk.Entry(boss_frame, textvariable=self.var_boss_name, width=40, font=("Segoe UI", 9)).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(boss_frame, text="Correo electrónico:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.var_boss_email = tk.StringVar()
        ttk.Entry(boss_frame, textvariable=self.var_boss_email, width=40, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(boss_frame, text="WhatsApp / Celular:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.var_boss_phone = tk.StringVar()
        ttk.Entry(boss_frame, textvariable=self.var_boss_phone, width=40, font=("Segoe UI", 9)).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        # 2. Sección Encargado
        sup_frame = ttk.LabelFrame(container, text="  👥 Datos de Encargado / Supervisor  ", padding=12)
        sup_frame.pack(fill="x", pady=(0, 16))

        ttk.Label(sup_frame, text="Nombre o Cargo:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self.var_sup_name = tk.StringVar(value="Encargado")
        ttk.Entry(sup_frame, textvariable=self.var_sup_name, width=40, font=("Segoe UI", 9)).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(sup_frame, text="Correo electrónico:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.var_sup_email = tk.StringVar()
        ttk.Entry(sup_frame, textvariable=self.var_sup_email, width=40, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(sup_frame, text="WhatsApp / Celular:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.var_sup_phone = tk.StringVar()
        ttk.Entry(sup_frame, textvariable=self.var_sup_phone, width=40, font=("Segoe UI", 9)).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        # 3. Sección Preferencias de Envío (Navegador y Outlook)
        pref_frame = ttk.LabelFrame(container, text="  🌐 Preferencias de Envío (Navegador y Correo)  ", padding=12)
        pref_frame.pack(fill="x", pady=(0, 16))

        ttk.Label(pref_frame, text="Navegador Web:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self.var_browser = tk.StringVar()
        self.combo_browser = ttk.Combobox(
            pref_frame,
            textvariable=self.var_browser,
            values=[
                "Detección automática (Detecta Opera / Chrome / Edge)",
                "Opera",
                "Google Chrome",
                "Microsoft Edge",
                "Predeterminado de Windows",
            ],
            state="readonly",
            font=("Segoe UI", 9),
            width=36,
        )
        self.combo_browser.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(pref_frame, text="Modo de Outlook:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.var_outlook = tk.StringVar()
        self.combo_outlook = ttk.Combobox(
            pref_frame,
            textvariable=self.var_outlook,
            values=[
                "🏢 Correo Corporativo OWA (correo.entelcc.cl)",
                "🌐 Outlook Web Office 365 (outlook.office.com)",
                "💻 Outlook de Escritorio (Aplicación instalada)",
            ],
            state="readonly",
            font=("Segoe UI", 9),
            width=36,
        )
        self.combo_outlook.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(pref_frame, text="URL Servidor OWA:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.var_owa_url = tk.StringVar(value="https://correo.entelcc.cl/owa")
        ttk.Entry(pref_frame, textvariable=self.var_owa_url, width=38, font=("Segoe UI", 9)).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        # 4. Créditos y Autoría del Sistema
        credits_frame = ttk.Frame(container)
        credits_frame.pack(fill="x", pady=(0, 14))
        lbl_author = ttk.Label(
            credits_frame,
            text=f"Desarrollado por {APP_AUTHOR} | {APP_AI_TOOL} (v{APP_VERSION})",
            font=("Segoe UI", 8, "italic"),
            foreground="#64748b",
        )
        lbl_author.pack(side="left")

        # 5. Botones inferiores
        btn_box = ttk.Frame(container)
        btn_box.pack(fill="x")

        btn_cancel = ttk.Button(btn_box, text="✕  Cancelar", style="Action.TButton", command=self.destroy, cursor="hand2")
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_save = ttk.Button(btn_box, text="💾  Guardar Configuración", style="Primary.TButton", command=self._save_data, cursor="hand2")
        btn_save.pack(side="right")

    def _load_current_data(self) -> None:
        data = self.settings_service.get_recipients_settings()
        self.var_boss_name.set(data.get("boss_name") or "Jefe Directo")
        self.var_boss_email.set(data.get("boss_email") or "")
        self.var_boss_phone.set(data.get("boss_phone") or "")

        self.var_sup_name.set(data.get("supervisor_name") or "Encargado")
        self.var_sup_email.set(data.get("supervisor_email") or "")
        self.var_sup_phone.set(data.get("supervisor_phone") or "")

        # Navegador preferido
        raw_browser = data.get("preferred_browser", "auto").lower()
        browser_map = {
            "auto": "Detección automática (Detecta Opera / Chrome / Edge)",
            "opera": "Opera",
            "chrome": "Google Chrome",
            "edge": "Microsoft Edge",
            "default": "Predeterminado de Windows",
        }
        self.var_browser.set(browser_map.get(raw_browser, browser_map["auto"]))

        # Modo de Outlook
        raw_outlook = data.get("outlook_mode", "owa").lower()
        outlook_map = {
            "owa": "🏢 Correo Corporativo OWA (correo.entelcc.cl)",
            "web": "🏢 Correo Corporativo OWA (correo.entelcc.cl)",
            "office365": "🌐 Outlook Web Office 365 (outlook.office.com)",
            "desktop": "💻 Outlook de Escritorio (Aplicación instalada)",
        }
        self.var_outlook.set(outlook_map.get(raw_outlook, outlook_map["owa"]))

        # URL OWA
        self.var_owa_url.set(data.get("owa_base_url") or "https://correo.entelcc.cl/owa")

    def _save_data(self) -> None:
        boss_email = self.var_boss_email.get().strip()
        boss_phone = self.var_boss_phone.get().strip()
        sup_email = self.var_sup_email.get().strip()
        sup_phone = self.var_sup_phone.get().strip()
        boss_name = self.var_boss_name.get().strip() or "Jefe Directo"
        sup_name = self.var_sup_name.get().strip() or "Encargado"

        # Mapeo inverso de navegador
        rev_browser_map = {
            "Detección automática (Detecta Opera / Chrome / Edge)": "auto",
            "Opera": "opera",
            "Google Chrome": "chrome",
            "Microsoft Edge": "edge",
            "Predeterminado de Windows": "default",
        }
        preferred_browser = rev_browser_map.get(self.var_browser.get(), "auto")

        # Mapeo inverso de Outlook
        rev_outlook_map = {
            "🏢 Correo Corporativo OWA (correo.entelcc.cl)": "owa",
            "🌐 Outlook Web Office 365 (outlook.office.com)": "office365",
            "💻 Outlook de Escritorio (Aplicación instalada)": "desktop",
        }
        outlook_mode = rev_outlook_map.get(self.var_outlook.get(), "owa")
        owa_base_url = self.var_owa_url.get().strip() or "https://correo.entelcc.cl/owa"

        ok = self.settings_service.save_recipients_settings(
            boss_email=boss_email,
            boss_phone=boss_phone,
            supervisor_email=sup_email,
            supervisor_phone=sup_phone,
            boss_name=boss_name,
            supervisor_name=sup_name,
            preferred_browser=preferred_browser,
            outlook_mode=outlook_mode,
            owa_base_url=owa_base_url,
        )

        if ok:
            messagebox.showinfo("Configuración Guardada", "Los datos de contacto y preferencias se han guardado exitosamente.", parent=self)
            if self.on_save_callback:
                self.on_save_callback(self.settings_service.get_recipients_settings())
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración en la base de datos.", parent=self)

    def _center_window(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        w = 550
        h = 600
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
