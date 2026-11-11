# app/utils/__init__.py
"""Utilidades compartidas del sistema."""
from .paths import get_app_data_dir, get_database_path, get_logs_dir, get_backups_dir
from .logger import setup_logger, get_logger

__all__ = [
    "get_app_data_dir",
    "get_database_path",
    "get_logs_dir",
    "get_backups_dir",
    "setup_logger",
    "get_logger",
]
