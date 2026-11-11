"""
MÓDULO REUTILIZABLE: app.utils.logger

DESCRIPCIÓN:
    Sistema centralizado de registro de eventos (logging) con rotación automática de archivos.

RESPONSABILIDAD:
    - Configurar y proveer loggers estructurados para toda la aplicación.
    - Asegurar que los errores técnicos, excepciones y eventos de auditoría se guarden en
      `%LOCALAPPDATA%\\<APP_NAME>\\logs\\app.log` con rotación por tamaño para no saturar disco.
    - Registrar eventos en consola durante desarrollo para retroalimentación inmediata.

DEPENDENCIAS:
    - logging, logging.handlers.RotatingFileHandler, sys
    - config.settings (LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_FORMAT, LOG_DATE_FORMAT)
    - app.utils.paths (get_log_file_path)

CONSUMIDORES:
    - Todos los módulos de app.models, app.services, app.controllers y app.views.

CÓMO EXTENDERLO:
    Para obtener un logger en cualquier clase o módulo:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Mensaje informativo")
"""

import logging
from logging.handlers import RotatingFileHandler
import sys

from config.settings import (
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)
from app.utils.paths import get_log_file_path

_initialized = False


def setup_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Inicializa el logger raíz de la aplicación con manejador de archivo rotativo y consola.
    Garantiza que la configuración se aplique una sola vez para evitar manejadores duplicados.
    """
    global _initialized
    root_logger = logging.getLogger("users_system")
    root_logger.setLevel(level)

    if _initialized:
        return root_logger

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # 1. Manejador de archivo rotativo en AppData (UTF-8)
    log_file = get_log_file_path()
    try:
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"No se pudo inicializar el archivo de log en {log_file}: {e}\n")

    # 2. Manejador de consola estándar
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    _initialized = True
    root_logger.info("Sistema de logging inicializado exitosamente.")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger secundario nombrado como hijo de 'users_system'.
    Ejemplo de uso:
        logger = get_logger(__name__)
    """
    if not _initialized:
        setup_logger()
    return logging.getLogger(f"users_system.{name}")
