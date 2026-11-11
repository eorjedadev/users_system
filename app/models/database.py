"""
PROYECTO: Sistema de Gestión de Usuarios, Documentación y Despacho Operativo
AUTOR: Eduardo Orjeda Figueroa | Lead Software Engineer & Prompt Engineer
METODOLOGÍA: AI-Augmented Software Engineering vía Google Gemini
MÓDULO: app.models.database

DESCRIPCIÓN:
    Gestor de persistencia SQLite3 con inicialización desatendida, migraciones de esquema
    y manejo seguro de transacciones.

RESPONSABILIDAD:
    - Gestionar el ciclo de vida de la base de datos `usuarios.db` en la ruta persistente.
    - Autocrecación de tablas e índices en la primera ejecución sin scripts manuales.
    - Apertura y validación de versión de esquema en ejecuciones posteriores preservando la información.
    - Proveer generadores de conexión con context managers (`row_factory = sqlite3.Row`).
    - Configurar pragmas críticos: `busy_timeout`, `journal_mode=WAL` y `foreign_keys=ON`.

DEPENDENCIAS:
    - sqlite3, pathlib.Path, typing.Optional, typing.Generator, contextlib.contextmanager
    - config.settings (DB_SCHEMA_VERSION, DB_BUSY_TIMEOUT_MS)
    - app.utils.paths (get_database_path)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.services.user_service
    - app.services.backup_service
    - main

CÓMO EXTENDERLO:
    Para nuevas migraciones de versión de esquema, agregar un método `_migrate_from_v<N>()`
    en la función `_check_or_migrate_schema()`.
"""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Generator, Optional

from config.settings import DB_BUSY_TIMEOUT_MS, DB_SCHEMA_VERSION
from app.utils.paths import get_database_path
from app.utils.logger import get_logger

logger = get_logger("database")

DDL_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT,
    rut TEXT,
    phone TEXT,
    email TEXT,
    area_or_group TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DDL_USER_ACCOUNTS_TABLE = """
CREATE TABLE IF NOT EXISTS user_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    is_primary INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, username)
);
"""

DDL_TICKETS_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS tickets_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT NOT NULL,
    user_id INTEGER,
    user_full_name TEXT NOT NULL,
    username TEXT,
    rut TEXT,
    phone TEXT,
    email TEXT,
    area_or_group TEXT,
    address TEXT,
    issue_detail TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
"""

DDL_APP_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_users_full_name ON users(full_name COLLATE NOCASE);",
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username COLLATE NOCASE);",
    "CREATE INDEX IF NOT EXISTS idx_users_rut ON users(rut);",
    "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);",
    "CREATE INDEX IF NOT EXISTS idx_user_accounts_user_id ON user_accounts(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_user_accounts_username ON user_accounts(username COLLATE NOCASE);",
    "CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets_log(created_at);",
    "CREATE INDEX IF NOT EXISTS idx_tickets_ticket_number ON tickets_log(ticket_number COLLATE NOCASE);",
]


class DatabaseManager:
    """Administrador centralizado de la conexión y persistencia local SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa el gestor con la ruta especificada o la ruta persistente por defecto.
        """
        self.db_path = db_path or get_database_path()
        self._ensure_initialized()

    def _get_raw_connection(self) -> sqlite3.Connection:
        """Crea una conexión con pragmas de rendimiento e integridad."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=DB_BUSY_TIMEOUT_MS / 1000.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        
        # Pragmas recomendados para SQLite local en Windows
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(f"PRAGMA busy_timeout = {DB_BUSY_TIMEOUT_MS};")
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
        except sqlite3.OperationalError:
            # En unidades de red o ciertas carpetas restringidas, WAL puede no ser soportado
            pass
        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager para obtener una conexión gestionada.
        Garantiza `commit` automático al salir del bloque o `rollback` en caso de excepción,
        y asegura el cierre de la conexión (`close()`).
        """
        conn = self._get_raw_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en transacción SQLite: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    def _ensure_initialized(self) -> None:
        """
        Verifica o inicializa la estructura de la base de datos de manera idempotente.
        Se ejecuta automáticamente al instanciar el DatabaseManager.
        """
        db_existed = self.db_path.exists() and self.db_path.stat().st_size > 0
        
        # Solo auto-sembrar si es la base de datos principal de producción (no en entornos de pruebas aislados)
        if not db_existed and self.db_path == get_database_path():
            self._try_seed_or_migrate()
            db_existed = self.db_path.exists() and self.db_path.stat().st_size > 0

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener versión actual
            cursor.execute("PRAGMA user_version;")
            current_version = cursor.fetchone()[0]

            # Crear tablas e índices de forma idempotente
            cursor.execute(DDL_USERS_TABLE)
            cursor.execute(DDL_USER_ACCOUNTS_TABLE)
            cursor.execute(DDL_TICKETS_LOG_TABLE)
            cursor.execute(DDL_APP_SETTINGS_TABLE)
            for idx_sql in DDL_INDEXES:
                cursor.execute(idx_sql)

            # Poblar de forma idempotente las cuentas existentes en user_accounts
            cursor.execute("""
                INSERT OR IGNORE INTO user_accounts (user_id, username, is_primary)
                SELECT id, username, 1 FROM users WHERE username IS NOT NULL AND TRIM(username) != '';
            """)

            # Si es la base de producción y no tiene usuarios, precargar datos maestros de la semilla
            if self.db_path == get_database_path():
                try:
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    if cursor.fetchone()[0] == 0:
                        self._populate_from_seed(cursor)
                        conn.commit()
                except Exception as e:
                    logger.debug(f"Verificación de precarga de semilla omitida: {e}")

            if not db_existed or current_version == 0:
                logger.info(f"Inicializando nueva base de datos en: {self.db_path}")
                cursor.execute(f"PRAGMA user_version = {DB_SCHEMA_VERSION};")
                logger.info(f"Esquema inicializado exitosamente (versión {DB_SCHEMA_VERSION}).")
            else:
                logger.info(
                    f"Base de datos existente conectada ({self.db_path}). "
                    f"Versión de esquema actual: {current_version}."
                )
                self._check_or_migrate_schema(conn, current_version)

    def _try_seed_or_migrate(self) -> None:
        """Intenta copiar la base de datos precargada desde assets o migrar desde la versión previa."""
        import os
        import shutil
        from app.utils.paths import get_assets_dir

        # 1. Semilla en assets (empaquetada en el ejecutable o proyecto)
        try:
            seed_path = get_assets_dir() / "seed_usuarios.db"
            if seed_path.exists() and seed_path.stat().st_size > 0:
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(seed_path, self.db_path)
                logger.info(f"Base de datos creada desde semilla de recursos: {seed_path}")
                return
        except Exception as e:
            logger.warning(f"No se pudo copiar base de datos semilla: {e}")

        # 2. Migración transparente desde la carpeta de la versión previa
        try:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                legacy_db = Path(local_app_data) / "GestionUsuariosDocumentos" / "data" / "usuarios.db"
                if legacy_db.exists() and legacy_db.stat().st_size > 0:
                    self.db_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(legacy_db, self.db_path)
                    logger.info(f"Base de datos migrada desde versión previa: {legacy_db}")
                    return
        except Exception as e:
            logger.warning(f"No se pudo migrar base de datos previa: {e}")

    def _populate_from_seed(self, cursor: sqlite3.Cursor) -> None:
        """Puebla los datos iniciales desde el archivo semilla si está disponible."""
        from app.utils.paths import get_assets_dir
        seed_path = get_assets_dir() / "seed_usuarios.db"
        if seed_path.exists() and seed_path.stat().st_size > 0:
            safe_seed = str(seed_path).replace("'", "''")
            cursor.execute(f"ATTACH DATABASE '{safe_seed}' AS seed_db;")
            cursor.execute("INSERT OR IGNORE INTO users SELECT * FROM seed_db.users;")
            cursor.execute("INSERT OR IGNORE INTO user_accounts SELECT * FROM seed_db.user_accounts;")
            cursor.execute("DETACH DATABASE seed_db;")
            logger.info("Usuarios maestros cargados desde semilla en usuarios.db")

    def _check_or_migrate_schema(self, conn: sqlite3.Connection, current_version: int) -> None:
        """
        Controla futuras migraciones de esquema incrementales sin pérdida de datos.
        """
        if current_version < DB_SCHEMA_VERSION:
            logger.info(f"Migrando esquema de versión {current_version} a {DB_SCHEMA_VERSION}...")
            # Aquí se ejecutarían scripts de alteración incremental cuando existan versiones futuras
            conn.execute(f"PRAGMA user_version = {DB_SCHEMA_VERSION};")
            logger.info("Migración de esquema completada.")
        elif current_version > DB_SCHEMA_VERSION:
            logger.warning(
                f"La base de datos tiene una versión ({current_version}) superior a la del código "
                f"({DB_SCHEMA_VERSION}). Se mantiene sin modificaciones."
            )

    def get_user_count(self) -> int:
        """Retorna la cantidad total de usuarios registrados."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users;")
            return cursor.fetchone()[0]
