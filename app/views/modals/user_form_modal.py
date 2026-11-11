"""
MÓDULO REUTILIZABLE: app.views.modals.user_form_modal

DESCRIPCIÓN:
    Ventana modal centrada para el registro (Agregar) o modificación (Editar) de usuarios.

RESPONSABILIDAD:
    - Desplegar formulario limpio para altas o precargado para ediciones.
    - Bloquear la interacción con la ventana padre mientras esté activa (`grab_set()`).
    - Atajos de teclado: `<Return>` guarda y `<Escape>` cancela.
    - Mantener los campos introducidos si la validación falla (evitar pérdida de datos).

DEPENDENCIAS:
    - tkinter, tkinter.ttk, typing.Optional, typing.Dict, typing.Any, typing.Callable
    - app.models.user (User)
"""

from typing import Any, Callable, Dict, Optional
import tkinter as tk
from tkinter import ttk

from app.models.user import User
from app.utils.window_utils import apply_app_icon


class UserFormModal(tk.Toplevel):
    """Diálogo modal para agregar o editar usuarios."""

    def __init__(
        self,
        parent: tk.Misc,
        mode: str = "add",
        user: Optional[User] = None,
        on_save: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        super().__init__(parent)
        self.mode = mode
        self.user = user
        self.on_save = on_save

        self.title("Nuevo Usuario" if mode == "add" else f"Editar Usuario — {user.full_name if user else ''}")
        self.resizable(False, False)
        self.configure(bg="#f8fafc")
        apply_app_icon(self)

        # Configuración modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_window(parent)

        self.bind("<Return>", lambda e: self._handle_save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Variables de formulario
        user_val = ""
        if self.user:
            if self.user.usernames:
                user_val = ", ".join(self.user.usernames)
            elif self.user.username:
                user_val = self.user.username

        self.var_name = tk.StringVar(value=self.user.full_name if self.user else "")
        self.var_user = tk.StringVar(value=user_val)
        self.var_rut = tk.StringVar(value=self.user.rut if self.user and self.user.rut else "")
        self.var_phone = tk.StringVar(value=self.user.phone if self.user and self.user.phone else "")
        self.var_email = tk.StringVar(value=self.user.email if self.user and self.user.email else "")
        self.var_area = tk.StringVar(value=self.user.area_or_group if self.user and self.user.area_or_group else "")
        self.var_address = tk.StringVar(value=self.user.address if self.user and self.user.address else "")

        fields = [
            ("Nombre completo *", self.var_name),
            ("Usuario(s) (separar con coma si tiene varios)", self.var_user),
            ("RUT (ej: 12345678-K)", self.var_rut),
            ("Teléfono", self.var_phone),
            ("Correo electrónico", self.var_email),
            ("Área o grupo", self.var_area),
            ("Dirección", self.var_address),
        ]

        self.entries = {}
        for row_idx, (label_text, var) in enumerate(fields):
            lbl = ttk.Label(main_frame, text=label_text, font=("Segoe UI", 9, "bold"), foreground="#334155")
            lbl.grid(row=row_idx * 2, column=0, sticky="w", pady=(4, 1))

            entry = ttk.Entry(main_frame, textvariable=var, font=("Segoe UI", 10), width=42)
            entry.grid(row=row_idx * 2 + 1, column=0, sticky="ew", pady=(0, 6))
            self.entries[label_text] = entry

        # Foco inicial en el primer campo
        self.entries["Nombre completo *"].focus_set()

        # Botones inferiores
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=len(fields) * 2, column=0, sticky="e", pady=(14, 0))

        btn_cancel = ttk.Button(btn_frame, text="✕  Cancelar", style="Action.TButton", command=self.destroy, cursor="hand2")
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_save = ttk.Button(
            btn_frame,
            text="💾  Guardar",
            style="Primary.TButton",
            command=self._handle_save,
            cursor="hand2",
        )
        btn_save.pack(side="right")

    def _handle_save(self) -> None:
        data = {
            "id": self.user.id if self.user else None,
            "full_name": self.var_name.get(),
            "username": self.var_user.get(),
            "usernames": self.var_user.get(),
            "rut": self.var_rut.get(),
            "phone": self.var_phone.get(),
            "email": self.var_email.get(),
            "area_or_group": self.var_area.get(),
            "address": self.var_address.get(),
        }
        if self.on_save:
            # Si el callback retorna True, se cierra la modal; si falla validación, permanece abierta
            success = self.on_save(data)
            if success:
                self.destroy()

    def _center_window(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
