# app/controllers/__init__.py
"""Paquete de controladores de la aplicacion."""
from .main_controller import MainController
from .user_controller import UserController
from .document_controller import DocumentController

__all__ = ["MainController", "UserController", "DocumentController"]
