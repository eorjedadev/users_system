"""
MÓDULO REUTILIZABLE: app.views.components.header_view

DESCRIPCIÓN:
    Barra superior estilizada y compacta de la aplicación.

RESPONSABILIDAD:
    - Desplegar la identidad visual del aplicativo en formato compacto.
    - Proveer acceso al Asistente de Importación CSV mediante botón con estilo de cabecera.
"""

from typing import Callable, Optional
import tkinter as tk
from tkinter import ttk

from config.settings import APP_SUBTITLE, APP_TITLE


class HeaderView(ttk.Frame):
    """Componente de cabecera visual compacto y moderno."""

    def __init__(
        self,
        parent: tk.Misc,
        on_import_csv: Optional[Callable[[], None]] = None,
        on_daily_report: Optional[Callable[[], None]] = None,
        on_settings: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, style="Header.TFrame", padding=(16, 8))
        self.on_import_csv = on_import_csv
        self.on_daily_report = on_daily_report
        self.on_settings = on_settings
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        # Panel de títulos (izquierda) con icono
        titles_frame = ttk.Frame(self, style="Header.TFrame")
        titles_frame.grid(row=0, column=0, sticky="w")

        title_lbl = ttk.Label(titles_frame, text=f"👥  {APP_TITLE}", style="HeaderTitle.TLabel")
        title_lbl.pack(anchor="w")

        subtitle_lbl = ttk.Label(titles_frame, text=APP_SUBTITLE, style="HeaderSubtitle.TLabel")
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Barra de botones superiores (derecha)
        right_box = ttk.Frame(self, style="Header.TFrame")
        right_box.grid(row=0, column=1, sticky="e")

        self.btn_daily_report = ttk.Button(
            right_box,
            text="📊  Reporte Diario",
            style="HeaderImport.TButton",
            command=self._handle_daily_report_click,
            cursor="hand2",
        )
        self.btn_daily_report.pack(side="left", padx=(0, 8))

        self.btn_settings = ttk.Button(
            right_box,
            text="⚙️  Destinatarios",
            style="HeaderImport.TButton",
            command=self._handle_settings_click,
            cursor="hand2",
        )
        self.btn_settings.pack(side="left", padx=(0, 8))

        self.btn_import = ttk.Button(
            right_box,
            text="📄  Importar CSV",
            style="HeaderImport.TButton",
            command=self._handle_import_click,
            cursor="hand2",
        )
        self.btn_import.pack(side="left")

    def _handle_import_click(self) -> None:
        if self.on_import_csv:
            self.on_import_csv()

    def _handle_daily_report_click(self) -> None:
        if self.on_daily_report:
            self.on_daily_report()

    def _handle_settings_click(self) -> None:
        if self.on_settings:
            self.on_settings()
