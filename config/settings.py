"""
PROYECTO: Sistema de Gestión de Usuarios, Documentación y Despacho Operativo
AUTOR: Eduardo Orjeda Figueroa
ROL: Lead Software Engineer & Prompt Engineer
METODOLOGÍA: AI-Augmented Software Engineering vía Google Gemini (Prompt Engineering)

DESCRIPCIÓN:
    Centraliza las constantes de la aplicación, configuración de ventanas,
    rutas relativas por defecto, nombres de persistencia y parámetros de logging.
"""

from pathlib import Path

# Metadatos del Sistema
APP_NAME = "GestionUsuarios"
APP_TITLE = "Gestión de Usuarios"
APP_SUBTITLE = "Administración local de Usuarios"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Eduardo Orjeda Figueroa"
APP_AI_TOOL = "Google Gemini (Advanced Prompt Engineering)"

# Persistencia SQLite
DB_FILENAME = "usuarios.db"
DB_SCHEMA_VERSION = 1
DB_BUSY_TIMEOUT_MS = 5000

# Archivos y Codificación
DEFAULT_ENCODING = "utf-8"
FALLBACK_ENCODINGS = ["utf-8-sig", "latin-1", "cp1252"]
TXT_EXTENSION = ".txt"
CSV_EXTENSION = ".csv"

# Dimensiones y Geometría de Interfaz Adaptable (Diseño Profesional 3 Columnas)
WINDOW_WIDTH = 1160
WINDOW_HEIGHT = 640
WINDOW_MIN_WIDTH = 960
WINDOW_MIN_HEIGHT = 540

# Configuración de Logging
LOG_FILENAME = "app.log"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | [%(name)s:%(lineno)d] | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
