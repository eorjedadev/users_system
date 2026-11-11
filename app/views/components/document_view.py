"""
MÓDULO REUTILIZABLE: app.views.components.document_view

DESCRIPCIÓN:
    Editor de documentos multilínea independiente con acciones de copiado y guardado.

RESPONSABILIDAD:
    - Proveer área de texto enriquecida con soporte multilínea y scrollbar vertical.
    - Mantener independencia total respecto al CRUD de usuarios.
    - Proveer casilla para combinar los datos del usuario seleccionado al momento de copiar/guardar.
    - Disparar callbacks independientes para cada acción.

DEPENDENCIAS:
    - tkinter, tkinter.ttk, typing.Optional, typing.Callable
"""

from typing import Callable, Optional
import tkinter as tk
from tkinter import ttk

PLACEHOLDER_DOC = "Escribe aquí la descripción, observación o detalle del problema..."


class DocumentView(tk.Frame):
    """Componente editor de documentos independiente con diseño visual refinado."""

    def __init__(
        self,
        parent: tk.Misc,
        on_copy: Optional[Callable[[], None]] = None,
        on_save_txt: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        on_record_ticket: Optional[Callable[[], None]] = None,
    ):
        super().__init__(
            parent,
            bg="#ffffff",
            highlightbackground="#dbe5ef",
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.on_copy = on_copy
        self.on_save_txt = on_save_txt
        self.on_clear = on_clear
        self.on_record_ticket = on_record_ticket
        self._placeholder_active = False

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # Editor de texto absorbe crecimiento

        # 1. Cabecera: Icono + Título + Campo para N° Ticket
        header_frame = tk.Frame(self, bg="#ffffff")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)

        lbl_title = tk.Label(
            header_frame,
            text="📄  Detalle del problema",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#0b2545",
        )
        lbl_title.grid(row=0, column=0, sticky="w")

        ticket_box = tk.Frame(header_frame, bg="#ffffff")
        ticket_box.grid(row=0, column=1, sticky="e")

        lbl_ticket = tk.Label(
            ticket_box,
            text="N° Ticket:",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#0b2545",
        )
        lbl_ticket.pack(side="left", padx=(0, 6))

        self.var_ticket_number = tk.StringVar()
        self.entry_ticket = ttk.Entry(
            ticket_box,
            textvariable=self.var_ticket_number,
            width=16,
            font=("Segoe UI", 9),
        )
        self.entry_ticket.pack(side="left")

        # 2. Editor de texto con Scrollbar vertical
        editor_container = tk.Frame(
            self,
            bg="#ffffff",
            highlightbackground="#cbd5e1",
            highlightthickness=1,
        )
        editor_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        editor_container.columnconfigure(0, weight=1)
        editor_container.rowconfigure(0, weight=1)

        self.text_widget = tk.Text(
            editor_container,
            wrap="word",
            undo=True,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#0f172a",
            insertbackground="#2563eb",
            selectbackground="#dbeafe",
            selectforeground="#1e40af",
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=8,
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(editor_container, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Placeholders
        self._set_placeholder()

        # 3. Barra inferior de botones de acción horizontales
        actions_bar = tk.Frame(self, bg="#ffffff")
        actions_bar.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.btn_record_ticket = ttk.Button(
            actions_bar,
            text="💾  Registrar Ticket",
            style="Primary.TButton",
            command=self._handle_record_ticket,
            cursor="hand2",
        )
        self.btn_record_ticket.pack(side="left", padx=(0, 8))

        self.btn_copy = ttk.Button(
            actions_bar,
            text="📋  Copiar texto",
            style="Outline.TButton",
            command=self._handle_copy,
            cursor="hand2",
        )
        self.btn_copy.pack(side="left", padx=(0, 8))

        self.btn_save = ttk.Button(
            actions_bar,
            text="📥  Guardar TXT",
            style="SaveDoc.TButton",
            command=self._handle_save,
            cursor="hand2",
        )
        self.btn_save.pack(side="left", padx=(0, 8))

        self.btn_clear_doc = ttk.Button(
            actions_bar,
            text="🧹  Limpiar",
            style="Outline.TButton",
            command=self._handle_clear,
            cursor="hand2",
        )
        self.btn_clear_doc.pack(side="left")

        # 4. Casilla de verificación
        self.var_include_user = tk.BooleanVar(value=False)
        self.chk_include_user = ttk.Checkbutton(
            self,
            text="Incluir los datos del usuario seleccionado en el documento",
            variable=self.var_include_user,
            cursor="hand2",
        )
        self.chk_include_user.grid(row=3, column=0, sticky="w")

    def _set_placeholder(self) -> None:
        self._placeholder_active = True
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", PLACEHOLDER_DOC)
        self.text_widget.configure(fg="#94a3b8")
        self.text_widget.bind("<FocusIn>", self._clear_placeholder)
        self.text_widget.bind("<FocusOut>", self._restore_placeholder)

    def _clear_placeholder(self, event=None) -> None:
        if self._placeholder_active:
            self._placeholder_active = False
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.configure(fg="#0f172a")

    def _restore_placeholder(self, event=None) -> None:
        content = self.text_widget.get("1.0", tk.END).strip()
        if not content:
            self._placeholder_active = True
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", PLACEHOLDER_DOC)
            self.text_widget.configure(fg="#94a3b8")

    def _handle_copy(self) -> None:
        if self.on_copy:
            self.on_copy()

    def _handle_save(self) -> None:
        if self.on_save_txt:
            self.on_save_txt()

    def _handle_clear(self) -> None:
        if self.on_clear:
            self.on_clear()

    def get_document_text(self) -> str:
        if self._placeholder_active:
            return ""
        return self.text_widget.get("1.0", tk.END).rstrip("\n")

    def set_document_text(self, text: str) -> None:
        self._placeholder_active = False
        self.text_widget.configure(fg="#0f172a")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)

    def clear_document(self) -> None:
        self._set_placeholder()

    def is_include_user_checked(self) -> bool:
        return self.var_include_user.get()

    def get_ticket_number(self) -> str:
        """Retorna el número de ticket ingresado."""
        return self.var_ticket_number.get().strip()

    def set_ticket_number(self, val: str) -> None:
        """Asigna el número de ticket en el campo de entrada."""
        self.var_ticket_number.set(val)

    def clear_ticket_number(self) -> None:
        """Limpia el campo de número de ticket."""
        self.var_ticket_number.set("")

    def _handle_record_ticket(self) -> None:
        """Maneja el evento de clic en Registrar Ticket."""
        if self.on_record_ticket:
            self.on_record_ticket()

