"""
MÓDULO REUTILIZABLE: app.views.main_window

DESCRIPCIÓN:
    Ventana principal de la aplicación Gestión de Usuarios y Documentos con arquitectura
    visual responsiva en dos columnas (Master-Detail).

RESPONSABILIDAD:
    - Ensamblar los componentes en una distribución ergonómica y adaptable a cualquier resolución:
      * Columna izquierda: Búsqueda y tabla de usuarios con scroll vertical.
      * Columna derecha: Ficha de usuario, barra de acciones CRUD y editor de documentos independiente.
    - Adaptar automáticamente las dimensiones de la ventana al tamaño de pantalla del usuario.
    - Asegurar que el editor de texto y la barra de estado siempre sean visibles sin desbordamiento.
    - Exponer referencias directas a sus subcomponentes para que el controlador asigne callbacks y estados.

DEPENDENCIAS:
    - tkinter, tkinter.ttk
    - config.settings (APP_TITLE, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH)
    - app.views.styles (configure_app_styles)
    - app.views.components.* (HeaderView, SearchView, UserCardView, ActionsView, DocumentView, StatusBarView)

CONSUMIDORES:
    - app.controllers.main_controller
    - main
"""

import tkinter as tk
from tkinter import ttk

from config.settings import (
    APP_TITLE,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from app.views.components.actions_view import ActionsView
from app.views.components.document_view import DocumentView
from app.views.components.header_view import HeaderView
from app.views.components.search_view import SearchView
from app.views.components.status_bar_view import StatusBarView
from app.views.components.user_card_view import UserCardView
from app.views.styles import configure_app_styles
from app.utils.window_utils import apply_app_icon, setup_windows_app_id


class MainWindow(tk.Tk):
    """Ventana principal adaptable con distribución responsiva en dos columnas."""

    def __init__(self):
        setup_windows_app_id()
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Aplicar icono del sistema corporativo en barra de título y barra de tareas
        apply_app_icon(self)

        # Aplicar diseño corporativo profesional
        self.app_style = configure_app_styles(self)

        self._build_layout()
        self._calculate_responsive_geometry()

    def _build_layout(self) -> None:
        """Organiza la interfaz en cabecera, barra de búsqueda flotante, 3 tarjetas laterales y barra de estado."""
        self.columnconfigure(0, weight=1)

        # Fila 0: Cabecera superior compacta
        self.rowconfigure(0, weight=0)
        self.header_view = HeaderView(self)
        self.header_view.grid(row=0, column=0, sticky="ew")

        # Fila 1: Barra de búsqueda flotante
        self.rowconfigure(1, weight=0)
        self.search_view = SearchView(self)
        self.search_view.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 8))

        # Fila 2: Cuerpo principal en 3 columnas (absorbe todo el crecimiento vertical)
        self.rowconfigure(2, weight=1)
        body_frame = ttk.Frame(self, style="TFrame")
        body_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))

        body_frame.columnconfigure(0, weight=38)  # Columna 1: Datos del usuario (~38%)
        body_frame.columnconfigure(1, weight=20)  # Columna 2: Acciones (~20%)
        body_frame.columnconfigure(2, weight=42)  # Columna 3: Detalle del problema (~42%)
        body_frame.rowconfigure(0, weight=1)

        # 1. Columna Izquierda: Ficha de datos del usuario
        self.user_card_view = UserCardView(body_frame)
        self.user_card_view.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # 2. Columna Central: Acciones CRUD
        self.actions_view = ActionsView(body_frame)
        self.actions_view.grid(row=0, column=1, sticky="nsew", padx=4)

        # 3. Columna Derecha: Detalle del problema (Editor de documento)
        self.document_view = DocumentView(body_frame)
        self.document_view.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # Fila 3: Barra de Estado inferior fija
        self.rowconfigure(3, weight=0)
        self.status_bar_view = StatusBarView(self)
        self.status_bar_view.grid(row=3, column=0, sticky="ew")

    def _calculate_responsive_geometry(self) -> None:
        """
        Calcula dimensiones proporcionadas a la resolución de pantalla actual
        para garantizar que todos los elementos sean visibles sin importar el escalado de Windows.
        """
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        target_w = min(1160, max(WINDOW_MIN_WIDTH, int(screen_w * 0.85)))
        target_h = min(640, max(WINDOW_MIN_HEIGHT, int(screen_h * 0.80)))

        x = max(0, (screen_w - target_w) // 2)
        y = max(0, (screen_h - target_h) // 2)

        self.geometry(f"{target_w}x{target_h}+{x}+{y}")

