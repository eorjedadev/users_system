"""
MÓDULO REUTILIZABLE: app.views.components.user_card_view

DESCRIPCIÓN:
    Ficha compacta de visualización de los datos del usuario en modo protegido de solo lectura.

RESPONSABILIDAD:
    - Desplegar organizadamente los 7 campos de la ficha en cuadrícula compacta de 2 columnas.
    - Mantener las entradas en `state='readonly'` para evitar alteraciones accidentales.
    - Proveer botón para deseleccionar y limpiar la ficha activa.

DEPENDENCIAS:
    - tkinter, tkinter.ttk, typing.Optional, typing.Callable
    - app.models.user (User)
"""

from typing import Callable, Dict, List, Optional
import tkinter as tk
from tkinter import ttk

from app.models.user import User

PLACEHOLDER_USER_COMBO = "Seleccione un usuario..."


class UserCardView(tk.Frame):
    """Ficha visual elegante para consulta protegida de datos de usuario."""

    def __init__(
        self,
        parent: tk.Misc,
        on_clear_selection: Optional[Callable[[], None]] = None,
        on_username_selected: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(
            parent,
            bg="#ffffff",
            highlightbackground="#dbe5ef",
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.on_clear_selection = on_clear_selection
        self.on_username_selected = on_username_selected
        self._current_user: Optional[User] = None
        self._current_user_id: Optional[int] = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # 1. Cabecera de la tarjeta: Icono + Título
        header_frame = tk.Frame(self, bg="#ffffff")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        lbl_title = tk.Label(
            header_frame,
            text="👤  Datos del usuario",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0b2545",
        )
        lbl_title.pack(anchor="w")

        # Variables reactivas
        self.var_name = tk.StringVar()
        self.var_user = tk.StringVar(value=PLACEHOLDER_USER_COMBO)
        self.var_rut = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_area = tk.StringVar()
        self.var_address = tk.StringVar()

        fields = [
            ("Nombre completo", self.var_name, "entry"),
            ("Usuario", self.var_user, "combo"),
            ("RUT", self.var_rut, "entry"),
            ("Teléfono", self.var_phone, "entry"),
            ("Correo", self.var_email, "entry"),
            ("Área o grupo", self.var_area, "entry"),
            ("Dirección", self.var_address, "entry"),
        ]

        self.entries: Dict[str, ttk.Widget] = {}

        for idx, (label_text, var, widget_type) in enumerate(fields, start=1):
            lbl = tk.Label(
                self,
                text=label_text,
                font=("Segoe UI", 8, "bold"),
                bg="#ffffff",
                fg="#1e293b",
                anchor="w",
                width=16,
            )
            lbl.grid(row=idx, column=0, sticky="w", pady=4, padx=(0, 6))

            if widget_type == "combo":
                # Combobox desplegable para seleccionar entre las múltiples cuentas del usuario
                combo = ttk.Combobox(
                    self,
                    textvariable=var,
                    font=("Segoe UI", 9),
                    style="Search.TCombobox",
                    state="readonly",
                )
                combo.grid(row=idx, column=1, sticky="ew", pady=4)
                combo.bind("<<ComboboxSelected>>", self._on_combo_select)
                self.combo_user = combo
                self.entries[label_text] = combo
            else:
                entry = ttk.Entry(
                    self,
                    textvariable=var,
                    font=("Segoe UI", 9),
                    style="Soft.TEntry",
                    state="readonly",
                )
                entry.grid(row=idx, column=1, sticky="ew", pady=4)
                self.entries[label_text] = entry

        # Botón Limpiar selección (inferior)
        self.btn_clear_sel = ttk.Button(
            self,
            text="🔄  Limpiar selección",
            style="Outline.TButton",
            command=self._handle_clear_click,
            cursor="hand2",
            state="disabled",
        )
        self.btn_clear_sel.grid(row=8, column=0, columnspan=2, sticky="w", pady=(12, 0))

    def _on_combo_select(self, event=None) -> None:
        selected_account = self.combo_user.get()
        if self._current_user:
            self._current_user.selected_username = selected_account
        if self.on_username_selected:
            self.on_username_selected(selected_account)

    def _handle_clear_click(self) -> None:
        self.clear_card()
        if self.on_clear_selection:
            self.on_clear_selection()

    def update_user_list(self, users: List[User]) -> None:
        """Compatibilidad con actualizaciones de lista."""
        pass

    def display_user(self, user: Optional[User]) -> None:
        """Muestra los datos del usuario en la ficha protegida y puebla sus cuentas asociadas."""
        if not user:
            self.clear_card()
            return

        self._current_user = user
        self._current_user_id = user.id
        self.var_name.set(user.full_name or "")

        # Poblar el Combobox con las cuentas que pertenecen a esta persona
        accounts = list(user.usernames) if user.usernames else ([user.username] if user.username else [])
        self.combo_user["values"] = accounts
        active_account = user.get_active_username() or (accounts[0] if accounts else "Sin usuario")
        self.var_user.set(active_account)
        user.selected_username = active_account

        self.var_rut.set(user.rut or "")
        self.var_phone.set(user.phone or "")
        self.var_email.set(user.email or "")
        self.var_area.set(user.area_or_group or "")
        self.var_address.set(user.address or "")
        self.btn_clear_sel.configure(state="normal")

    def clear_card(self) -> None:
        """Vacia los campos y desactiva el botón de limpieza."""
        self._current_user = None
        self._current_user_id = None
        self.var_name.set("")
        self.combo_user["values"] = []
        self.var_user.set(PLACEHOLDER_USER_COMBO)
        self.var_rut.set("")
        self.var_phone.set("")
        self.var_email.set("")
        self.var_area.set("")
        self.var_address.set("")
        self.btn_clear_sel.configure(state="disabled")

    def get_current_user_id(self) -> Optional[int]:
        return self._current_user_id

    def get_selected_username(self) -> str:
        return self.var_user.get()

