"""
MÓDULO REUTILIZABLE: app.services.user_service

DESCRIPCIÓN:
    Servicio de negocio para la gestión de usuarios y operaciones CRUD en SQLite.

RESPONSABILIDAD:
    - Centralizar la lógica de persistencia de usuarios (altas, modificaciones, eliminaciones y consultas).
    - Desacoplar completamente a las vistas y controladores de las consultas SQL.
    - Ejecutar validaciones previas antes de insertar o actualizar registros en SQLite.
    - Optimizar búsquedas multicampo sobre grandes volúmenes de usuarios utilizando los índices creados.

DEPENDENCIAS:
    - typing.Optional, typing.List, typing.Tuple
    - app.models.user (User)
    - app.models.database (DatabaseManager)
    - app.services.validation_service (ValidationService)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.controllers.user_controller
    - app.services.csv_service

CÓMO EXTENDERLO:
    Para agregar filtros por área o paginación avanzada, implementar métodos adicionales
    como `get_users_by_area()` o `get_paginated_users(limit, offset)`.
"""

from typing import List, Optional, Tuple

from app.models.database import DatabaseManager
from app.models.user import User
from app.services.validation_service import ValidationService
from app.utils.logger import get_logger

logger = get_logger("user_service")


class UserService:
    """Servicio de gestión y operaciones de persistencia sobre la entidad Usuario."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    @staticmethod
    def _parse_usernames(raw: Any) -> List[str]:
        """Extrae y normaliza una lista única de cuentas de usuario."""
        if not raw:
            return []
        if isinstance(raw, list):
            res = []
            for item in raw:
                val = str(item).strip()
                if val and val not in res:
                    res.append(val)
            return res
        parts = [p.strip() for p in str(raw).split(",") if p.strip()]
        res = []
        for p in parts:
            if p not in res:
                res.append(p)
        return res

    def _attach_user_accounts(self, conn: sqlite3.Connection, user: User) -> None:
        """Carga las cuentas/usuarios asociados desde user_accounts en el objeto User."""
        if not user.id:
            return
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username FROM user_accounts WHERE user_id = ? ORDER BY is_primary DESC, id ASC;",
            (user.id,)
        )
        accounts = [r[0] for r in cursor.fetchall() if r[0]]
        if not accounts and user.username:
            accounts = [user.username]
        user.usernames = accounts
        user.selected_username = accounts[0] if accounts else user.username

    def get_total_count(self) -> int:
        """Retorna el total de usuarios registrados en el sistema."""
        return self.db.get_user_count()

    def get_all_users(self, limit: int = 200, offset: int = 0) -> List[User]:
        """Retorna la lista de usuarios ordenados alfabéticamente por nombre."""
        query = """
            SELECT id, full_name, username, rut, phone, email, area_or_group, address, created_at, updated_at
            FROM users
            ORDER BY full_name COLLATE NOCASE ASC
            LIMIT ? OFFSET ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit, offset))
            users = [User.from_row(row) for row in cursor.fetchall()]
            for u in users:
                self._attach_user_accounts(conn, u)
            return users

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su identificador interno único."""
        query = """
            SELECT id, full_name, username, rut, phone, email, area_or_group, address, created_at, updated_at
            FROM users
            WHERE id = ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            user = User.from_row(row)
            self._attach_user_accounts(conn, user)
            return user

    def search_users(self, search_term: str, limit: int = 100) -> List[User]:
        """
        Busca coincidencias insensibles a mayúsculas/minúsculas en Nombre, Cuentas de Usuario, RUT, Teléfono y Correo.
        Si el término está vacío, retorna los primeros `limit` usuarios.
        """
        term = search_term.strip()
        if not term:
            return self.get_all_users(limit=limit)

        like_pattern = f"%{term}%"
        query = """
            SELECT DISTINCT u.id, u.full_name, u.username, u.rut, u.phone, u.email, u.area_or_group, u.address, u.created_at, u.updated_at
            FROM users u
            LEFT JOIN user_accounts ua ON u.id = ua.user_id
            WHERE u.full_name LIKE ?
               OR u.username LIKE ?
               OR ua.username LIKE ?
               OR u.rut LIKE ?
               OR u.phone LIKE ?
               OR u.email LIKE ?
            ORDER BY u.full_name COLLATE NOCASE ASC
            LIMIT ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (like_pattern, like_pattern, like_pattern, like_pattern, like_pattern, like_pattern, limit))
            users = [User.from_row(row) for row in cursor.fetchall()]
            for u in users:
                self._attach_user_accounts(conn, u)
            return users

    def create_user(self, user_data: dict) -> Tuple[bool, Optional[User], str]:
        """
        Crea un nuevo usuario en la base de datos tras validar sus campos.

        Retorna:
            Tuple[bool, Optional[User], str]: (éxito, usuario_creado, mensaje)
        """
        is_valid, errors = ValidationService.validate_user(user_data)
        if not is_valid:
            return (False, None, "\n".join(errors))

        clean = ValidationService.normalize_user_data(user_data)
        usernames_list = self._parse_usernames(user_data.get("usernames") or user_data.get("username"))
        if usernames_list:
            clean["username"] = usernames_list[0]

        query = """
            INSERT INTO users (full_name, username, rut, phone, email, area_or_group, address)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (
                        clean["full_name"],
                        clean["username"],
                        clean["rut"],
                        clean["phone"],
                        clean["email"],
                        clean["area_or_group"],
                        clean["address"],
                    ),
                )
                new_id = cursor.lastrowid

                # Guardar todas las cuentas asociadas en user_accounts
                for idx, uname in enumerate(usernames_list):
                    cursor.execute(
                        "INSERT OR IGNORE INTO user_accounts (user_id, username, is_primary) VALUES (?, ?, ?);",
                        (new_id, uname, 1 if idx == 0 else 0)
                    )

                logger.info(f"Usuario creado exitosamente con ID={new_id}: '{clean['full_name']}' con cuentas {usernames_list}")

            created_user = self.get_user_by_id(new_id)
            return (True, created_user, "Usuario agregado exitosamente.")
        except Exception as e:
            logger.error(f"Error al insertar usuario: {e}", exc_info=True)
            return (False, None, f"Error interno al guardar en base de datos: {e}")

    def update_user(self, user_data: dict) -> Tuple[bool, Optional[User], str]:
        """
        Actualiza un usuario existente respetando su ID interno y sincronizando sus cuentas.

        Retorna:
            Tuple[bool, Optional[User], str]: (éxito, usuario_actualizado, mensaje)
        """
        user_id = user_data.get("id")
        if not user_id:
            return (False, None, "No se especificó un ID de usuario válido para actualizar.")

        is_valid, errors = ValidationService.validate_user(user_data)
        if not is_valid:
            return (False, None, "\n".join(errors))

        clean = ValidationService.normalize_user_data(user_data)
        usernames_list = self._parse_usernames(user_data.get("usernames") or user_data.get("username"))
        if usernames_list:
            clean["username"] = usernames_list[0]

        query = """
            UPDATE users
            SET full_name = ?,
                username = ?,
                rut = ?,
                phone = ?,
                email = ?,
                area_or_group = ?,
                address = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (
                        clean["full_name"],
                        clean["username"],
                        clean["rut"],
                        clean["phone"],
                        clean["email"],
                        clean["area_or_group"],
                        clean["address"],
                        user_id,
                    ),
                )
                if cursor.rowcount == 0:
                    return (False, None, f"No se encontró ningún usuario con el ID {user_id}.")

                # Sincronizar cuentas en user_accounts
                cursor.execute("DELETE FROM user_accounts WHERE user_id = ?;", (user_id,))
                for idx, uname in enumerate(usernames_list):
                    cursor.execute(
                        "INSERT OR IGNORE INTO user_accounts (user_id, username, is_primary) VALUES (?, ?, ?);",
                        (user_id, uname, 1 if idx == 0 else 0)
                    )

                logger.info(f"Usuario ID={user_id} actualizado exitosamente con cuentas {usernames_list}.")

            updated_user = self.get_user_by_id(user_id)
            return (True, updated_user, "Usuario actualizado exitosamente.")
        except Exception as e:
            logger.error(f"Error al actualizar usuario ID={user_id}: {e}", exc_info=True)
            return (False, None, f"Error interno al actualizar en base de datos: {e}")

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Elimina un usuario de la base de datos por su ID.

        Retorna:
            Tuple[bool, str]: (éxito, mensaje)
        """
        existing = self.get_user_by_id(user_id)
        if not existing:
            return (False, f"El usuario con ID {user_id} no existe.")

        query = "DELETE FROM users WHERE id = ?;"
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                logger.info(f"Usuario eliminado exitosamente: ID={user_id} ('{existing.full_name}')")
            return (True, f"Usuario '{existing.full_name}' eliminado exitosamente.")
        except Exception as e:
            logger.error(f"Error al eliminar usuario ID={user_id}: {e}", exc_info=True)
            return (False, f"Error al eliminar el registro: {e}")

