# app/models/__init__.py
"""Paquete de modelos y persistencia."""
from .user import User
from .database import DatabaseManager

__all__ = ["User", "DatabaseManager"]
