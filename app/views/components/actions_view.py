"""
MÓDULO REUTILIZABLE: app.views.components.actions_view

DESCRIPCIÓN:
    Barra horizontal de botones de acción para operaciones CRUD sobre usuarios.

RESPONSABILIDAD:
    - Desplegar botones de acción en formato horizontal compacto y ergonómico.
    - Habilitar o deshabilitar reactivamente las acciones según el estado de selección activa.
    - Despachar eventos a sus respectivos callbacks.

DEPENDENCIAS:
    - tkinter, tkinter.ttk, typing.Optional, typing.Callable
"""

from typing import Callable, Optional
import tkinter as tk
from tkinter import ttk


class ActionsView(tk.Frame):
    """Tarjeta vertical de acciones CRUD para usuarios según maqueta de referencia."""

    def __init__(
        self,
        parent: tk.Misc,
        on_add: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[], None]] = None,
        on_delete: Optional[Callable[[], None]] = None,
    ):
        super().__init__(
            parent,
            bg="#ffffff",
            highlightbackground="#dbe5ef",
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        # 1. Cabecera: Icono + Título
        header_frame = tk.Frame(self, bg="#ffffff")
        header_frame.grid(row=0, column=0, sticky="w", pady=(0, 14))

        lbl_title = tk.Label(
            header_frame,
            text="⚙  Acciones",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0b2545",
        )
        lbl_title.pack(anchor="w")

        # 2. Botón 1: ＋ Agregar usuario (Verde sólido)
        self.btn_add = ttk.Button(
            self,
            text="＋  Agregar usuario",
            style="AddUser.TButton",
            command=self._handle_add,
            cursor="hand2",
        )
        self.btn_add.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        # 3. Botón 2: ✎ Editar usuario (Celeste claro con borde azul)
        self.btn_edit = ttk.Button(
            self,
            text="✎  Editar usuario",
            style="EditUser.TButton",
            command=self._handle_edit,
            cursor="hand2",
            state="disabled",
        )
        self.btn_edit.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        # 4. Botón 3: 🗑 Eliminar usuario (Rojo claro con borde rojo)
        self.btn_delete = ttk.Button(
            self,
            text="🗑  Eliminar usuario",
            style="DeleteUser.TButton",
            command=self._handle_delete,
            cursor="hand2",
            state="disabled",
        )
        self.btn_delete.grid(row=3, column=0, sticky="ew", pady=(0, 14))

        # 5. Texto de ayuda informativa
        hint_frame = tk.Frame(self, bg="#ffffff")
        hint_frame.grid(row=4, column=0, sticky="w")

        lbl_hint = tk.Label(
            hint_frame,
            text="ⓘ  Editar y eliminar requieren\n    seleccionar un usuario.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#0284c7",
            justify="left",
        )
        lbl_hint.pack(anchor="w")

    def _handle_add(self) -> None:
        if self.on_add:
            self.on_add()

    def _handle_edit(self) -> None:
        if self.on_edit:
            self.on_edit()

    def _handle_delete(self) -> None:
        if self.on_delete:
            self.on_delete()

    def set_selection_state(self, has_selection: bool) -> None:
        state = "normal" if has_selection else "disabled"
        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)

