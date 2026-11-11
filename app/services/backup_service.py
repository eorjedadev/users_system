"""
MÓDULO REUTILIZABLE: app.services.backup_service

DESCRIPCIÓN:
    Servicio de copias de seguridad en caliente (Online Backup) para SQLite.

RESPONSABILIDAD:
    - Crear copias atómicas y seguras del archivo de base de datos antes de operaciones masivas
      o destructivas (importación CSV o eliminación de registros).
    - Rotar copias de seguridad antiguas para conservar espacio en disco.
    - Utilizar la API nativa `sqlite3.Connection.backup()` para garantizar que la copia sea consistente
      incluso con transacciones activas o modo WAL.

DEPENDENCIAS:
    - sqlite3, datetime, pathlib.Path, typing.Optional, typing.List
    - app.models.database (DatabaseManager)
    - app.utils.paths (get_backups_dir)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.services.csv_service
    - app.services.user_service

CÓMO EXTENDERLO:
    Para programar copias periódicas o automáticas al inicio, invocar `create_backup(reason="startup")`.
"""

from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Optional

from app.models.database import DatabaseManager
from app.utils.paths import get_backups_dir
from app.utils.logger import get_logger

logger = get_logger("backup_service")


class BackupService:
    """Servicio para creación y rotación de copias de seguridad de SQLite."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None, max_backups: int = 5):
        self.db_manager = db_manager or DatabaseManager()
        self.max_backups = max_backups
        self.backups_dir = get_backups_dir()

    def create_backup(self, reason: str = "auto") -> Optional[Path]:
        """
        Genera una copia de seguridad en caliente de la base de datos actual.

        Args:
            reason: Motivo de la copia (ej. 'pre_import', 'pre_delete', 'manual').

        Retorna:
            Path al archivo de copia creado, o None si no se pudo crear.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"usuarios_backup_{timestamp}_{reason}.db"
        backup_path = self.backups_dir / backup_filename

        try:
            with self.db_manager.get_connection() as src_conn:
                dest_conn = sqlite3.connect(str(backup_path))
                try:
                    src_conn.backup(dest_conn)
                    logger.info(f"Copia de seguridad generada con éxito: {backup_path.name}")
                finally:
                    dest_conn.close()

            self._rotate_backups()
            return backup_path
        except Exception as e:
            logger.error(f"Error generando copia de seguridad: {e}", exc_info=True)
            return None

    def _rotate_backups(self) -> None:
        """Elimina copias de seguridad antiguas conservando solo las `max_backups` más recientes."""
        try:
            backup_files = sorted(
                self.backups_dir.glob("usuarios_backup_*.db"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if len(backup_files) > self.max_backups:
                for file_to_remove in backup_files[self.max_backups :]:
                    file_to_remove.unlink()
                    logger.info(f"Copia de seguridad antigua rotada/eliminada: {file_to_remove.name}")
        except Exception as e:
            logger.warning(f"Error durante la rotación de copias de seguridad: {e}")
