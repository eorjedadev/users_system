"""
MÓDULO REUTILIZABLE: app.models.ticket

DESCRIPCIÓN:
    Entidad de dominio para el registro de atenciones y tickets de soporte técnico.

RESPONSABILIDAD:
    - Encapsular los datos del ticket asociado a un usuario y a un detalle de problema.
    - Proveer métodos de serialización, deserialización desde sqlite3.Row y formateo
      para Outlook y WhatsApp.
"""

from dataclasses import dataclass
import sqlite3
from typing import Any, Dict, Optional


@dataclass
class Ticket:
    """Entidad que representa una atención o ticket registrado en el sistema."""

    id: Optional[int] = None
    ticket_number: str = ""
    user_id: Optional[int] = None
    user_full_name: str = ""
    username: Optional[str] = None
    rut: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    area_or_group: Optional[str] = None
    address: Optional[str] = None
    issue_detail: str = ""
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad en un diccionario plano."""
        return {
            "id": self.id,
            "ticket_number": self.ticket_number,
            "user_id": self.user_id,
            "user_full_name": self.user_full_name,
            "username": self.username,
            "rut": self.rut,
            "phone": self.phone,
            "email": self.email,
            "area_or_group": self.area_or_group,
            "address": self.address,
            "issue_detail": self.issue_detail,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Ticket":
        """Crea una instancia de Ticket a partir de una fila de sqlite3.Row."""
        keys = row.keys() if hasattr(row, "keys") else []
        return cls(
            id=row["id"] if "id" in keys else None,
            ticket_number=row["ticket_number"] if "ticket_number" in keys else "",
            user_id=row["user_id"] if "user_id" in keys else None,
            user_full_name=row["user_full_name"] if "user_full_name" in keys else "",
            username=row["username"] if "username" in keys else None,
            rut=row["rut"] if "rut" in keys else None,
            phone=row["phone"] if "phone" in keys else None,
            email=row["email"] if "email" in keys else None,
            area_or_group=row["area_or_group"] if "area_or_group" in keys else None,
            address=row["address"] if "address" in keys else None,
            issue_detail=row["issue_detail"] if "issue_detail" in keys else "",
            created_at=row["created_at"] if "created_at" in keys else None,
        )

    def get_time_str(self) -> str:
        """Extrae la hora y minutos (HH:MM) del created_at si está disponible."""
        if not self.created_at:
            return ""
        if hasattr(self.created_at, "strftime"):
            return self.created_at.strftime("%H:%M")
        val_str = str(self.created_at)
        if len(val_str) >= 16:
            return val_str[11:16]
        return ""

    def format_for_email_block(self, index: int) -> str:
        """Formatea el ticket individual para el reporte consolidado de correo."""
        time_part = f" ({self.get_time_str()} hrs)" if self.get_time_str() else ""
        lines = [
            f"Ticket #{index}: {self.ticket_number}{time_part}",
            f"Usuario: {self.user_full_name}" + (f" ({self.username})" if self.username else ""),
        ]
        detalles = []
        if self.rut:
            detalles.append(f"RUT: {self.rut}")
        if self.area_or_group:
            detalles.append(f"Área: {self.area_or_group}")
        if self.phone:
            detalles.append(f"Fono: {self.phone}")
        if self.email:
            detalles.append(f"Correo: {self.email}")

        if detalles:
            lines.append(" | ".join(detalles))

        lines.append("Detalle del problema:")
        lines.append(self.issue_detail or "Sin detalle registrado.")
        lines.append("-" * 50)
        return "\n".join(lines)

    def format_for_whatsapp_block(self, index: int) -> str:
        """Formatea el ticket individual con formato Markdown de WhatsApp."""
        time_part = f" ({self.get_time_str()})" if self.get_time_str() else ""
        lines = [
            f"🔹 *Ticket #{index}: {self.ticket_number}*{time_part}",
            f"*Usuario:* {self.user_full_name}" + (f" (`{self.username}`)" if self.username else ""),
        ]
        info_items = []
        if self.area_or_group:
            info_items.append(f"*Área:* {self.area_or_group}")
        if self.phone:
            info_items.append(f"*Fono:* {self.phone}")
        if info_items:
            lines.append(" | ".join(info_items))

        lines.append(f"*Detalle:* {self.issue_detail or 'Sin detalle registrado.'}")
        lines.append("────────────────────")
        return "\n".join(lines)
