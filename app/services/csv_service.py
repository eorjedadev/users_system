"""
MÓDULO REUTILIZABLE: app.services.csv_service

DESCRIPCIÓN:
    Servicio integral para la inspección, vista previa, validación y carga masiva de archivos CSV.

RESPONSABILIDAD:
    - Detectar automáticamente la codificación y delimitador del archivo CSV de origen sin asumir UTF-8.
    - Preservar el archivo CSV original en modo de solo lectura (nunca modificar el archivo fuente).
    - Ejecutar copia de seguridad previa de la base de datos antes de iniciar la importación.
    - Mapear las columnas de origen hacia el esquema de la aplicación.
    - Insertar los registros válidos dentro de una transacción SQLite masiva.
    - Generar un informe detallado con cantidades de registros importados, nulos y advertencias.

DEPENDENCIAS:
    - csv, pathlib.Path, dataclasses, typing.Optional, typing.List, typing.Dict, typing.Tuple
    - app.models.database (DatabaseManager)
    - app.services.validation_service (ValidationService)
    - app.services.backup_service (BackupService)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.controllers.main_controller
    - app.views.modals.csv_import_modal

CÓMO EXTENDERLO:
    Para incorporar reglas de mapeo personalizadas definidas por el usuario desde la UI,
    pasar un diccionario `custom_mapping` al método `import_csv_data()`.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import DEFAULT_ENCODING, FALLBACK_ENCODINGS
from app.models.database import DatabaseManager
from app.services.backup_service import BackupService
from app.services.validation_service import ValidationService
from app.utils.logger import get_logger

logger = get_logger("csv_service")


@dataclass
class CsvInspectionResult:
    """Estructura con los resultados de la inspección preliminar de un archivo CSV."""

    filepath: Path
    encoding: str
    delimiter: str
    headers: List[str]
    total_rows: int
    sample_rows: List[Dict[str, str]] = field(default_factory=list)
    proposed_mapping: Dict[str, str] = field(default_factory=dict)
    unmapped_columns: List[str] = field(default_factory=list)


@dataclass
class CsvImportSummary:
    """Resumen de resultados tras la ejecución de una importación masiva."""

    total_read: int = 0
    imported_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    backup_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)


class CsvService:
    """Servicio de procesamiento e importación de archivos CSV hacia SQLite."""

    TARGET_FIELDS = [
        "full_name",
        "username",
        "rut",
        "phone",
        "email",
        "area_or_group",
        "address",
    ]

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.backup_service = BackupService(self.db)

    @classmethod
    def detect_encoding(cls, filepath: Path) -> str:
        """Determina la codificación de caracteres del archivo probando las opciones autorizadas."""
        candidates = [DEFAULT_ENCODING] + FALLBACK_ENCODINGS
        for enc in candidates:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    # Leer hasta 64KB para verificar decodificación completa
                    f.read(65536)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        return "latin-1"  # Fallback seguro que no lanza UnicodeDecodeError

    @classmethod
    def detect_dialect(cls, filepath: Path, encoding: str) -> csv.Dialect:
        """Determina delimitador y entrecomillado del CSV usando `csv.Sniffer`."""
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            sample = f.read(8192)
            try:
                sniffer = csv.Sniffer()
                return sniffer.sniff(sample)
            except csv.Error:
                # Si falla el sniffer, usar delimitador estándar por coma
                class FallbackDialect(csv.excel):
                    delimiter = ","

                return FallbackDialect()

    def inspect_csv(self, filepath: Path) -> CsvInspectionResult:
        """
        Inspecciona el archivo CSV sin modificarlo y propone el mapeo de columnas.
        """
        encoding = self.detect_encoding(filepath)
        dialect = self.detect_dialect(filepath, encoding)

        headers: List[str] = []
        sample_rows: List[Dict[str, str]] = []
        total_rows = 0

        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            reader = csv.DictReader(f, delimiter=dialect.delimiter)
            headers = [h.strip() for h in (reader.fieldnames or [])]
            for row in reader:
                total_rows += 1
                if len(sample_rows) < 5:
                    sample_rows.append({k.strip(): (v.strip() if v else "") for k, v in row.items()})

        # Mapeo propuesto automático basado en nombres comunes
        mapping = {}
        unmapped = []
        for h in headers:
            h_clean = h.lower().strip()
            if h_clean in ("full_name", "nombre", "nombre_completo", "nombre completo"):
                mapping["full_name"] = h
            elif h_clean in ("username", "usuario", "login", "cuenta"):
                mapping["username"] = h
            elif h_clean in ("rut", "run", "identificador", "cedula"):
                mapping["rut"] = h
            elif h_clean in ("phone", "telefono", "teléfono", "fono", "celular"):
                mapping["phone"] = h
            elif h_clean in ("email", "correo", "mail", "correo_electronico"):
                mapping["email"] = h
            elif h_clean in ("area_or_group", "area", "área", "departamento", "grupo"):
                mapping["area_or_group"] = h
            elif h_clean in ("address", "direccion", "dirección", "sucursal", "ubicacion"):
                mapping["address"] = h
            else:
                unmapped.append(h)

        return CsvInspectionResult(
            filepath=filepath,
            encoding=encoding,
            delimiter=dialect.delimiter,
            headers=headers,
            total_rows=total_rows,
            sample_rows=sample_rows,
            proposed_mapping=mapping,
            unmapped_columns=unmapped,
        )

    def import_csv_data(
        self, filepath: Path, column_mapping: Optional[Dict[str, str]] = None
    ) -> CsvImportSummary:
        """
        Ejecuta la importación del CSV hacia SQLite.
        
        Garantías:
            - Copia de seguridad en caliente previa.
            - Preserva el CSV original.
            - Ejecución en transacción única masiva.
            - Sanitización de 'NULL' y espacios.
        """
        summary = CsvImportSummary()

        # 1. Copia de seguridad previa obligatoria
        backup_file = self.backup_service.create_backup(reason="pre_csv_import")
        summary.backup_path = backup_file

        inspection = self.inspect_csv(filepath)
        mapping = column_mapping or inspection.proposed_mapping

        if "full_name" not in mapping:
            raise ValueError("El archivo CSV no cuenta con una columna asignada para 'full_name' (Nombre Completo).")

        users_to_insert: List[Tuple[Any, ...]] = []

        with open(filepath, "r", encoding=inspection.encoding, errors="replace") as f:
            reader = csv.DictReader(f, delimiter=inspection.delimiter)
            
            for row_num, row in enumerate(reader, start=2):
                summary.total_read += 1

                # Extraer según mapeo
                full_name_val = row.get(mapping["full_name"], "")
                sanitized_name = ValidationService.sanitize_field(full_name_val)

                if not sanitized_name:
                    summary.skipped_count += 1
                    summary.warnings.append(f"Fila {row_num}: Omitida por carecer de nombre completo.")
                    continue

                username_val = ValidationService.sanitize_field(row.get(mapping.get("username", "")))
                rut_val = ValidationService.sanitize_field(row.get(mapping.get("rut", "")))
                phone_val = ValidationService.sanitize_field(row.get(mapping.get("phone", "")))
                email_val = ValidationService.sanitize_field(row.get(mapping.get("email", "")))
                area_val = ValidationService.sanitize_field(row.get(mapping.get("area_or_group", "")))
                addr_val = ValidationService.sanitize_field(row.get(mapping.get("address", "")))

                # Formatear RUT si existe
                if rut_val:
                    rut_val = rut_val.upper()

                users_to_insert.append(
                    (
                        sanitized_name,
                        username_val,
                        rut_val,
                        phone_val,
                        email_val,
                        area_val,
                        addr_val,
                    )
                )

        # 2. Inserción masiva transaccional en SQLite
        insert_query = """
            INSERT INTO users (full_name, username, rut, phone, email, area_or_group, address)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(insert_query, users_to_insert)
                summary.imported_count = len(users_to_insert)
                logger.info(
                    f"Importación masiva completada: {summary.imported_count} usuarios insertados "
                    f"desde {filepath.name}"
                )
        except Exception as e:
            logger.error(f"Error crítico durante la importación masiva: {e}", exc_info=True)
            summary.error_count += 1
            summary.warnings.append(f"Fallo durante inserción transaccional: {e}")
            raise

        return summary
