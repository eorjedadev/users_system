"""
MÓDULO REUTILIZABLE: app.services.ticket_service

DESCRIPCIÓN:
    Servicio de lógica de negocio para registrar, consultar y consolidar tickets de atención
    en reportes diarios para jefatura.

RESPONSABILIDAD:
    - Registrar un nuevo ticket asociado o no a un usuario en la tabla tickets_log de SQLite.
    - Consultar tickets registrados por fecha (ayer, hoy o fechas personalizadas).
    - Formatear el reporte consolidado diario para Outlook y WhatsApp con la estructura corporativa.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from app.models.database import DatabaseManager
from app.models.ticket import Ticket
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("ticket_service")


class TicketService:
    """Servicio para la gestión y reporte diario de tickets de atención."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def record_ticket(
        self,
        ticket_number: str,
        user: Optional[User],
        issue_detail: str,
    ) -> Tuple[bool, str, Optional[Ticket]]:
        """
        Registra una nueva atención en la base de datos local.

        Retorna:
            Tuple[bool, str, Optional[Ticket]]: (éxito, mensaje, ticket_creado)
        """
        clean_ticket_no = ticket_number.strip()
        clean_detail = issue_detail.strip()

        if not clean_ticket_no:
            return (False, "Debe ingresar el número de ticket proporcionado por su ticketera.", None)

        if not clean_detail and not user:
            return (False, "Debe ingresar una descripción del problema o seleccionar un usuario.", None)

        user_id = user.id if user else None
        user_name = user.full_name if user else "Usuario no registrado"
        username = user.get_active_username() if user else None
        rut = user.rut if user else None
        phone = user.phone if user else None
        email = user.email if user else None
        area = user.area_or_group if user else None
        address = user.address if user else None

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Si user_id fue provisto, verificar que exista en users para no violar integridad referencial
                if user_id is not None:
                    cursor.execute("SELECT 1 FROM users WHERE id = ?;", (user_id,))
                    if not cursor.fetchone():
                        user_id = None

                sql = """
                    INSERT INTO tickets_log (
                        ticket_number, user_id, user_full_name, username, rut, phone, email, area_or_group, address, issue_detail, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """
                cursor.execute(
                    sql,
                    (clean_ticket_no, user_id, user_name, username, rut, phone, email, area, address, clean_detail),
                )
                conn.commit()
                new_id = cursor.lastrowid
                
                # Recuperar fila creada
                cursor.execute("SELECT * FROM tickets_log WHERE id = ?;", (new_id,))
                row = cursor.fetchone()
                ticket = Ticket.from_row(row) if row else None

                logger.info(f"Ticket registrado con éxito ID={new_id} N°='{clean_ticket_no}' para '{user_name}'.")
                return (True, f"Ticket #{clean_ticket_no} registrado exitosamente.", ticket)

        except Exception as e:
            logger.error(f"Error al registrar ticket #{clean_ticket_no}: {e}", exc_info=True)
            return (False, f"Error al guardar el ticket en la base de datos: {e}", None)

    def get_tickets_for_date(self, target_date: date) -> List[Ticket]:
        """
        Recupera todos los tickets registrados en la fecha especificada (YYYY-MM-DD).
        """
        date_str = target_date.strftime("%Y-%m-%d")
        sql = """
            SELECT * FROM tickets_log
            WHERE date(created_at) = ?
            ORDER BY id ASC;
        """
        tickets: List[Ticket] = []
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (date_str,))
                for row in cursor.fetchall():
                    tickets.append(Ticket.from_row(row))
        except Exception as e:
            logger.error(f"Error al consultar tickets para la fecha {date_str}: {e}", exc_info=True)

        return tickets

    def get_yesterday_tickets(self) -> Tuple[date, List[Ticket]]:
        """Recupera la fecha de ayer y los tickets registrados ese día."""
        yesterday = date.today() - timedelta(days=1)
        return (yesterday, self.get_tickets_for_date(yesterday))

    def get_today_tickets(self) -> Tuple[date, List[Ticket]]:
        """Recupera la fecha de hoy y los tickets registrados en la jornada."""
        today = date.today()
        return (today, self.get_tickets_for_date(today))

    def get_total_ticket_count(self) -> int:
        """Retorna el número total histórico de tickets guardados."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tickets_log;")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    @classmethod
    def format_daily_report_email(cls, tickets: List[Ticket], report_date: date) -> str:
        """
        Genera el texto consolidado del reporte diario para enviar por Outlook.
        """
        date_str = report_date.strftime("%d/%m/%Y")
        total = len(tickets)

        lines = [
            f"REPORTE DIARIO DE ATENCIONES Y TICKETS",
            f"Fecha de Gestión: {date_str}",
            f"Total de Atenciones Realizadas: {total}",
            "=" * 60,
            "",
        ]

        if not tickets:
            lines.append("No se registraron atenciones ni tickets en la fecha indicada.")
        else:
            for i, t in enumerate(tickets, start=1):
                lines.append(t.format_for_email_block(i))
                lines.append("")

            lines.append("=" * 60)
            lines.append(f"Fin del reporte. Total tickets gestionados: {total}")

        return "\n".join(lines)

    @classmethod
    def format_daily_report_whatsapp(cls, tickets: List[Ticket], report_date: date) -> str:
        """
        Genera el texto consolidado del reporte diario para WhatsApp con formato enriquecido.
        """
        date_str = report_date.strftime("%d/%m/%Y")
        total = len(tickets)

        lines = [
            f"📋 *REPORTE DIARIO DE ATENCIONES*",
            f"🗓️ *Fecha:* {date_str}",
            f"🔢 *Total Tickets:* {total}",
            "────────────────────",
        ]

        if not tickets:
            lines.append("_No se registraron tickets en esta fecha._")
        else:
            for i, t in enumerate(tickets, start=1):
                lines.append(t.format_for_whatsapp_block(i))

            lines.append(f"✅ *Resumen:* {total} ticket(s) completado(s).")

        return "\n".join(lines)
