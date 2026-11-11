"""
MÓDULO REUTILIZABLE: app.utils.window_utils

DESCRIPCIÓN:
    Utilidades visuales y de integración con el sistema operativo para ventanas Tkinter.

RESPONSABILIDAD:
    - Registrar el identificador explícito de aplicación en Windows (AppUserModelID)
      para que la barra de tareas y el menú de Windows muestren el icono corporativo.
    - Aplicar el icono institucional (.ico y .png) a ventanas principales y modales Toplevel,
      eliminando permanentemente el icono de pluma por defecto de Tkinter.
"""

import sys
import tkinter as tk

from app.utils.paths import get_app_icon_ico_path, get_app_icon_png_path


def setup_windows_app_id() -> None:
    """Configura el identificador explícito de proceso en Windows."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            app_id = "pytrix.gestionusuarios.desktop.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass


def apply_app_icon(window: tk.Misc) -> None:
    """
    Aplica el icono oficial del sistema a la ventana especificada.
    Configura tanto el icono nativo .ico de Windows como la imagen .png
    para asegurar compatibilidad con diferentes resoluciones y temas.
    """
    ico_path = get_app_icon_ico_path()
    if ico_path.exists():
        try:
            # En Tk raíz se puede usar default=str(ico_path) para que aplique a todas las ventanas
            if isinstance(window, tk.Tk):
                window.iconbitmap(default=str(ico_path))
            else:
                window.iconbitmap(str(ico_path))
        except Exception:
            try:
                window.wm_iconbitmap(str(ico_path))
            except Exception:
                pass

    png_path = get_app_icon_png_path()
    if png_path.exists():
        try:
            photo = tk.PhotoImage(file=str(png_path))
            # Guardar referencia en el widget para evitar recolección de basura
            setattr(window, "_app_icon_photo_ref", photo)
            window.iconphoto(True, photo)
        except Exception:
            pass
