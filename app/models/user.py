"""
MÓDULO REUTILIZABLE: app.models.user

DESCRIPCIÓN:
    Representación del dominio para la entidad Usuario (Data Transfer Object / Entity).

RESPONSABILIDAD:
    - Encapsular los datos de un usuario en un objeto tipado e inmutable por defecto.
    - Proveer métodos de serialización a diccionario, deserialización desde filas SQLite (sqlite3.Row)
      y generación del bloque de texto formateado para documentos combinados.

DEPENDENCIAS:
    - dataclasses.dataclass
    - typing.Optional, typing.Dict, typing.Any
    - sqlite3.Row

CONSUMIDORES:
    - app.models.database
    - app.services.user_service
    - app.services.csv_service
    - app.services.document_service
    - app.controllers.*
    - app.views.*

CÓMO EXTENDERLO:
    Para agregar nuevos campos a la ficha (ej. cargo o estado), añadirlos como atributos opcionales
    con valor por defecto `None`, actualizando `to_dict`, `from_row` y `to_formatted_text`.
"""

from dataclasses import dataclass, field
import sqlite3
from typing import Any, Dict, List, Optional


@dataclass
class User:
    """Entidad que representa un registro de usuario en el sistema."""

    id: Optional[int] = None
    full_name: str = ""
    username: Optional[str] = None
    rut: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    area_or_group: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    usernames: List[str] = field(default_factory=list)
    selected_username: Optional[str] = None

    def get_active_username(self) -> str:
        """Retorna el usuario actualmente seleccionado, el primario o el primero de sus cuentas."""
        if self.selected_username:
            return self.selected_username
        if self.username:
            return self.username
        if self.usernames:
            return self.usernames[0]
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un diccionario plano."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "rut": self.rut,
            "phone": self.phone,
            "email": self.email,
            "area_or_group": self.area_or_group,
            "address": self.address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "usernames": list(self.usernames),
            "selected_username": self.get_active_username(),
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        """Instancia un User a partir de una fila retornada por sqlite3.Row."""
        return cls(
            id=row["id"] if "id" in row.keys() else None,
            full_name=row["full_name"] or "",
            username=row["username"],
            rut=row["rut"],
            phone=row["phone"],
            email=row["email"],
            area_or_group=row["area_or_group"],
            address=row["address"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
            updated_at=row["updated_at"] if "updated_at" in row.keys() else None,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Instancia un User a partir de un diccionario."""
        return cls(
            id=data.get("id"),
            full_name=data.get("full_name", "").strip(),
            username=data.get("username"),
            rut=data.get("rut"),
            phone=data.get("phone"),
            email=data.get("email"),
            area_or_group=data.get("area_or_group"),
            address=data.get("address"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_formatted_text(self) -> str:
        """
        Genera el bloque textual limpio y estandarizado para adjuntar a documentos TXT
        o copiar al portapapeles.
        """
        def format_val(val: Optional[str]) -> str:
            return val.strip() if val and val.strip() not in ("", "NULL", "None") else "No registrado"

        lines = [
            "Resumen del usuario",
            f"Nombre completo: {self.full_name}",
            f"Usuario: {format_val(self.get_active_username())}",
            f"RUT: {format_val(self.rut)}",
            f"Telefono: {format_val(self.phone)}",
            f"Correo electronico: {format_val(self.email)}",
            f"Area o grupo: {format_val(self.area_or_group)}",
            f"Direccion: {format_val(self.address)}",
        ]
        return "\n".join(lines)
