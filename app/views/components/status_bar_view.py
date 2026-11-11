"""
MÓDULO REUTILIZABLE: app.views.components.status_bar_view

DESCRIPCIÓN:
    Barra de estado inferior informativa, estilizada y compacta.

RESPONSABILIDAD:
    - Informar el estado de la conexión SQLite persistente.
    - Mostrar el conteo total de usuarios registrados en tiempo real.
    - Desplegar la identidad del usuario actualmente seleccionado en la ficha.

DEPENDENCIAS:
    - tkinter, tkinter.ttk, typing.Optional
"""

from typing import Optional
import tkinter as tk
from tkinter import ttk


class StatusBarView(ttk.Frame):
    """Barra de estado inferior informativa compacta y estilizada."""

    def __init__(self, parent: tk.Misc):
        super().__init__(parent, style="Status.TFrame", padding=(16, 4))
        self._current_count = 0
        self._current_sel_id: Optional[int] = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Sección 1: Estado Base de Datos (izquierda)
        self.lbl_db = ttk.Label(
            self,
            text="🗄  Base de datos: usuarios.db (Conectada)",
            style="StatusDb.TLabel",
            anchor="w",
        )
        self.lbl_db.grid(row=0, column=0, sticky="w")

        # Sección 2: Conteo y Selección (derecha)
        self.lbl_info = ttk.Label(
            self,
            text="Total usuarios: 0          |          Selección ID: —",
            style="StatusText.TLabel",
            anchor="e",
        )
        self.lbl_info.grid(row=0, column=1, sticky="e")

    def _refresh_info_text(self) -> None:
        count_str = f"{self._current_count:,}".replace(",", ".")
        sel_str = f"#{self._current_sel_id}" if self._current_sel_id else "—"
        self.lbl_info.configure(text=f"Total usuarios: {count_str}          |          Selección ID: {sel_str}")

    def update_db_status(self, text: str) -> None:
        # Si el texto no tiene icono, añadir 🗄
        if "Base de datos" in text and "🗄" not in text:
            text = f"🗄  {text.replace('🟢 ', '')}"
        self.lbl_db.configure(text=text)

    def update_user_count(self, count: int) -> None:
        self._current_count = count
        self._refresh_info_text()

    def update_selected_user(self, full_name: Optional[str] = None, user_id: Optional[int] = None) -> None:
        self._current_sel_id = user_id
        self._refresh_info_text()

