"""
MÓDULO REUTILIZABLE: app.services.validation_service

DESCRIPCIÓN:
    Servicio de validación y sanitización de datos de entrada para la entidad Usuario.

RESPONSABILIDAD:
    - Aplicar las reglas de negocio acordadas en la Etapa 3 (Análisis Funcional).
    - Verificar la validez de los datos introducidos manualmente en formularios o leídos de CSV.
    - Sanitizar cadenas de texto (normalizar espacios, tratar 'NULL' como None, formatear RUT en mayúsculas).
    - Generar mensajes de error claros y accionables para el usuario.

DEPENDENCIAS:
    - re, typing.Tuple, typing.List, typing.Dict, typing.Any, typing.Optional

CONSUMIDORES:
    - app.services.user_service
    - app.services.csv_service
    - app.controllers.user_controller

CÓMO EXTENDERLO:
    Para incorporar nuevas reglas de campo, añadir un método de validación específico
    `_validate_<campo>()` y llamarlo dentro de `validate_user()`.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class ValidationService:
    """Servicio de validación sintáctica y de reglas de negocio para usuarios."""

    # Expresiones regulares de validación permisiva
    _EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    _RUT_FLEXIBLE_REGEX = re.compile(r"^(?:(\d{1,2}(?:\.\d{3}){2})|(\d{7,8}))-([\dkK])$")
    _PHONE_ALLOWED_CHARS = re.compile(r"^[\d\s\+\-\/\(\)\.]{3,35}$")

    ALL_FIELDS = ["full_name", "username", "rut", "phone", "email", "area_or_group", "address"]

    @classmethod
    def sanitize_field(cls, value: Optional[str]) -> Optional[str]:
        """
        Limpia un campo de texto: recorta espacios y convierte cadenas vacías o
        literales 'NULL'/'None' a `None` de Python.
        """
        if value is None:
            return None
        cleaned = str(value).strip()
        if cleaned == "" or cleaned.upper() in ("NULL", "NONE"):
            return None
        return cleaned

    @classmethod
    def normalize_user_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza y normaliza un diccionario de datos de usuario asegurando todas las claves."""
        normalized: Dict[str, Any] = {"id": None}
        if "id" in data and data["id"] is not None:
            val_id = str(data["id"]).strip()
            normalized["id"] = int(val_id) if val_id.isdigit() else None

        for field in cls.ALL_FIELDS:
            sanitized = cls.sanitize_field(data.get(field))
            if field == "rut" and sanitized:
                sanitized = sanitized.upper()
            normalized[field] = sanitized

        return normalized

    @classmethod
    def validate_user(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida los datos de un usuario según la matriz de validación aprobada.

        Retorna:
            Tuple[bool, List[str]]: (es_valido, lista_de_mensajes_de_error)
        """
        errors: List[str] = []
        clean = cls.normalize_user_data(data)

        # 1. Nombre completo (Obligatorio, mínimo 3 caracteres)
        full_name = clean.get("full_name")
        if not full_name:
            errors.append("El nombre completo es obligatorio.")
        elif len(full_name) < 3:
            errors.append("El nombre completo debe tener al menos 3 caracteres.")

        # 2. Correo (Opcional, pero si se ingresa debe tener formato válido)
        email = clean.get("email")
        if email:
            if not cls._EMAIL_REGEX.match(email):
                errors.append(f"El correo '{email}' no tiene un formato válido (ejemplo: usuario@dominio.cl).")

        # 3. RUT (Opcional, pero si se ingresa debe cumplir formato básico)
        rut = clean.get("rut")
        if rut:
            # Limpiar puntos si los tuviera para comprobación flexible
            rut_sin_puntos = rut.replace(".", "")
            if not re.match(r"^\d{7,8}-[\dK]$", rut_sin_puntos):
                errors.append(f"El RUT '{rut}' no tiene un formato reconocido (ejemplo: 12345678-K).")

        # 4. Teléfono (Opcional, caracteres numéricos y separadores autorizados)
        phone = clean.get("phone")
        if phone:
            if not cls._PHONE_ALLOWED_CHARS.match(phone):
                errors.append(f"El teléfono '{phone}' contiene caracteres no permitidos.")

        # 5. Usuario (Opcional, longitud máxima razonable)
        username = clean.get("username")
        if username and len(username) > 60:
            errors.append("El nombre de usuario excede los 60 caracteres.")

        return (len(errors) == 0, errors)
