"""
MÓDULO REUTILIZABLE: app.views.components.search_view

DESCRIPCIÓN:
    Panel de búsqueda y lista de usuarios navegable con tabla interactiva Treeview.

RESPONSABILIDAD:
    - Proveer caja de entrada de búsqueda con atajo <Return>.
    - Mostrar lista completa o filtrada de usuarios con scrollbar vertical responsivo.
    - Notificar mediante callbacks cuando el usuario ejecuta una búsqueda o selecciona una fila.
    - Aplicar resaltado y filas alternadas para alta legibilidad.

DEPENDENCIAS:
    - tkinter, tkinter.ttk, typing.Optional, typing.List, typing.Callable
    - app.models.user (User)
"""

from typing import Callable, List, Optional
import tkinter as tk
from tkinter import ttk

from app.models.user import User

PLACEHOLDER_SEARCH = "Buscar por nombre, usuario, RUT o correo..."


class SearchView(tk.Frame):
    """Barra horizontal de búsqueda directa con campo de texto y botón Buscar."""

    def __init__(
        self,
        parent: tk.Misc,
        on_search: Optional[Callable[[str], None]] = None,
        on_user_selected: Optional[Callable[[int], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
    ):
        super().__init__(
            parent,
            bg="#ffffff",
            highlightbackground="#dbe5ef",
            highlightthickness=1,
            padx=14,
            pady=8,
        )
        self.on_search = on_search
        self.on_user_selected = on_user_selected
        self.on_clear = on_clear

        self._placeholder_active = False
        self._users_list: List[User] = []

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.rowconfigure(0, weight=1)

        # 1. Icono y Título
        lbl_title = tk.Label(
            self,
            text="🔍  Buscar usuario",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0b2545",
        )
        lbl_title.grid(row=0, column=0, padx=(2, 12), sticky="w")

        # 2. Entrada de texto para búsqueda directa (sin Combobox)
        self.search_entry = ttk.Entry(
            self,
            font=("Segoe UI", 9),
            style="Soft.TEntry",
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        # Atajo Enter para buscar inmediatamente
        self.search_entry.bind("<Return>", lambda e: self._trigger_search())

        # 3. Botón directo de Buscar con icono 🔍
        self.btn_search = ttk.Button(
            self,
            text="🔍",
            style="SearchIcon.TButton",
            command=self._trigger_search,
            cursor="hand2",
            width=3,
        )
        self.btn_search.grid(row=0, column=2, padx=(0, 4))

        # 4. Botón de Actualizar / Refrescar con icono 🔄
        self.btn_clear = ttk.Button(
            self,
            text="🔄",
            style="RefreshIcon.TButton",
            command=self._handle_clear,
            cursor="hand2",
            width=3,
        )
        self.btn_clear.grid(row=0, column=3)
        self.btn_refresh = self.btn_clear

        self._set_placeholder()

    def _set_placeholder(self) -> None:
        self._placeholder_active = True
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, PLACEHOLDER_SEARCH)
        self.search_entry.configure(foreground="#94a3b8")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)

    def _clear_placeholder(self, event=None) -> None:
        if self._placeholder_active:
            self._placeholder_active = False
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground="#0f172a")

    def _restore_placeholder(self, event=None) -> None:
        if not self.search_entry.get().strip():
            self._placeholder_active = True
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, PLACEHOLDER_SEARCH)
            self.search_entry.configure(foreground="#94a3b8")

    def _trigger_search(self) -> None:
        query = self.get_query()
        if self.on_search:
            self.on_search(query)

    def _handle_clear(self) -> None:
        self.search_entry.delete(0, tk.END)
        self._set_placeholder()
        if self.on_clear:
            self.on_clear()

    def get_query(self) -> str:
        if self._placeholder_active:
            return ""
        return self.search_entry.get().strip()

    def set_query(self, text: str) -> None:
        self._placeholder_active = False
        self.search_entry.configure(foreground="#0f172a")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, text)

    def populate_results(self, users: List[User]) -> None:
        """Conserva la lista de resultados para navegación o consultas."""
        self._users_list = users

    def select_user_in_tree(self, user_id: int) -> None:
        """Compatibilidad con el controlador al seleccionar usuario."""
        pass

    def clear_tree_selection(self) -> None:
        """Restaura el estado inicial del buscador."""
        self._restore_placeholder()

