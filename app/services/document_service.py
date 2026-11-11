"""
MÓDULO REUTILIZABLE: app.services.document_service

DESCRIPCIÓN:
    Servicio para la composición, copiado y exportación a disco de documentos en formato TXT.

RESPONSABILIDAD:
    - Gestionar el guardado de archivos de texto con codificación UTF-8 y saltos de línea Windows.
    - Manejar la interacción con el portapapeles del sistema operativo de manera segura.
    - Proveer la lógica de combinación en memoria de la ficha de usuario y el documento redactado,
      asegurando que el editor original no sea alterado ni sobrescrito.

DEPENDENCIAS:
    - pathlib.Path, typing.Optional, typing.Tuple, tkinter
    - app.models.user (User)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.controllers.document_controller

CÓMO EXTENDERLO:
    Para exportar a otros formatos (ej. Markdown o HTML), agregar métodos `save_as_markdown()`
    o `generate_html_report()`.
"""

from pathlib import Path
from typing import Optional, Tuple
import tkinter as tk

from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("document_service")


class DocumentService:
    """Servicio de lógica de negocio para la gestión de documentos independientes."""

    @classmethod
    def combine_document(cls, user: Optional[User], text_content: str, include_user: bool) -> str:
        """
        Combina los datos del usuario con el texto del documento según el estado de la casilla.
        Si include_user es True y hay un usuario válido, antepone el bloque 'Resumen del usuario'
        seguido del encabezado 'Detalle del problema:' y la observación redactada.
        Si include_user es False, retorna únicamente el texto redactado.
        """
        text = text_content.strip()
        if not include_user or not user:
            return text

        user_block = user.to_formatted_text()
        if text:
            return f"{user_block}\nDetalle del problema:\n{text}"
        return f"{user_block}\nDetalle del problema:"

    @classmethod
    def copy_to_clipboard(cls, root_widget: tk.Misc, content: str) -> Tuple[bool, str]:
        """
        Copia la cadena especificada al portapapeles del sistema operativo.

        Retorna:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not content.strip():
            return (False, "No hay texto para copiar en el documento.")

        try:
            root_widget.clipboard_clear()
            root_widget.clipboard_append(content)
            # Asegura que el portapapeles conserve el contenido tras salir del foco
            root_widget.update()
            logger.info("Contenido copiado exitosamente al portapapeles de Windows.")
            return (True, "Contenido copiado al portapapeles exitosamente.")
        except Exception as e:
            logger.error(f"Error al copiar al portapapeles: {e}", exc_info=True)
            return (False, f"No se pudo copiar al portapapeles: {e}")

    @classmethod
    def save_to_txt_file(cls, filepath: Path, content: str) -> Tuple[bool, str]:
        """
        Guarda el contenido en un archivo de texto en disco con codificación UTF-8.

        Retorna:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not content.strip():
            return (False, "No se puede guardar un documento vacío.")

        try:
            # Asegurar extensión .txt
            target_path = filepath if filepath.suffix.lower() == ".txt" else filepath.with_suffix(".txt")

            # Escribir con saltos de línea consistentes y UTF-8
            with open(target_path, "w", encoding="utf-8", newline="\r\n") as f:
                f.write(content)

            logger.info(f"Documento guardado exitosamente en: {target_path}")
            return (True, f"Documento guardado exitosamente en:\n{target_path}")
        except PermissionError:
            logger.error(f"Permiso denegado al escribir en {filepath}")
            return (False, "Permiso denegado. No tiene autorización para escribir en esta ubicación.")
        except Exception as e:
            logger.error(f"Error al guardar documento TXT: {e}", exc_info=True)
            return (False, f"Ocurrió un error al guardar el archivo: {e}")
