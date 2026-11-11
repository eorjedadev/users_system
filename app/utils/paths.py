"""
MÓDULO REUTILIZABLE: app.utils.paths

DESCRIPCIÓN:
    Gestor de rutas del sistema y persistencia segura en entornos Windows y compilados.

RESPONSABILIDAD:
    - Resolver las rutas absolutas donde se almacenan la base de datos SQLite, los registros (logs)
      y las copias de seguridad (backups), garantizando permisos de escritura en Windows (%LOCALAPPDATA%).
    - Resolver la ruta base de recursos empaquetados por PyInstaller (sys._MEIPASS) o en desarrollo.
    - Asegurar la existencia física de las carpetas requeridas antes de su uso.

DEPENDENCIAS:
    - os, sys, pathlib.Path
    - config.settings (APP_NAME, DB_FILENAME, LOG_FILENAME)

CONSUMIDORES:
    - app.models.database
    - app.utils.logger
    - app.services.backup_service
    - main

CÓMO EXTENDERLO:
    Para añadir nuevas rutas persistentes (ej. plantillas o exportaciones), crear una función
    `get_<recurso>_dir()` que invoque `get_app_data_dir() / "<subcarpeta>"` y asegure `mkdir()`.
"""

import os
import sys
from pathlib import Path

from config.settings import APP_NAME, DB_FILENAME, LOG_FILENAME


def get_bundle_dir() -> Path:
    """
    Retorna la ruta base donde residen los archivos del ejecutable o del código fuente.
    
    En desarrollo: Retorna la raíz del proyecto.
    En PyInstaller: Retorna la carpeta temporal sys._MEIPASS o el directorio del .exe.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent.parent.parent


def get_app_data_dir() -> Path:
    """
    Retorna la ruta raíz persistente de la aplicación en el directorio de usuario de Windows.
    
    Ubicación estándar:
        C:\\Users\\<Usuario>\\AppData\\Local\\<APP_NAME>
    
    Si %LOCALAPPDATA% no está disponible, utiliza la carpeta del usuario como fallback.
    Crea la carpeta automáticamente si no existe.
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data) / APP_NAME
    else:
        base_dir = Path.home() / "AppData" / "Local" / APP_NAME

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_database_dir() -> Path:
    """Retorna y asegura el directorio donde reside la base de datos SQLite."""
    data_dir = get_app_data_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path() -> Path:
    """Retorna la ruta absoluta al archivo SQLite persistente (usuarios.db)."""
    return get_database_dir() / DB_FILENAME


def get_logs_dir() -> Path:
    """Retorna y asegura el directorio donde se almacenan los archivos de log."""
    logs_dir = get_app_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_log_file_path() -> Path:
    """Retorna la ruta absoluta al archivo de log activo."""
    return get_logs_dir() / LOG_FILENAME


def get_backups_dir() -> Path:
    """Retorna y asegura el directorio de copias de seguridad de la base de datos."""
    backups_dir = get_app_data_dir() / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def get_assets_dir() -> Path:
    """Retorna la ruta al directorio de recursos estáticos e iconos."""
    return get_bundle_dir() / "assets"


def get_app_icon_ico_path() -> Path:
    """Retorna la ruta al icono nativo de Windows (.ico)."""
    return get_assets_dir() / "app_icon.ico"


def get_app_icon_png_path() -> Path:
    """Retorna la ruta al icono en alta resolución (.png)."""
    return get_assets_dir() / "app_icon.png"
