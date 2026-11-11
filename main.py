"""
PROYECTO: Sistema de Gestión de Usuarios, Documentación y Despacho Operativo
AUTOR: Eduardo Orjeda Figueroa
ROL: Lead Software Engineer & Prompt Engineer
METODOLOGÍA: AI-Augmented Software Engineering vía Google Gemini (Prompt Engineering)
ARQUITECTURA: MVC Estricto con Persistencia SQLite y GUI Tkinter/ttk

DESCRIPCIÓN:
    Inicializa el entorno de la aplicación, el sistema de logging centralizado,
    la captura global de excepciones no controladas y arranca el MainController.

RESPONSABILIDAD:
    - Configurar el registro de eventos al inicio.
    - Atrapar cualquier excepción crítica para evitar cierres silenciosos o mostrar trazas crudas.
    - Instanciar y ejecutar el MainController.
"""

import sys
import tkinter as tk
from tkinter import messagebox

from app.controllers.main_controller import MainController
from app.utils.logger import get_logger, setup_logger


def main() -> int:
    """Función principal de inicialización y ejecución del programa."""
    # 1. Inicializar sistema de logging en AppData y consola
    setup_logger()
    logger = get_logger("main")
    logger.info("==================================================")
    logger.info("Iniciando aplicación: Gestión de Usuarios y Documentos")
    logger.info("==================================================")

    try:
        # 2. Instanciar y arrancar el controlador principal
        app = MainController()
        app.run()
        logger.info("Aplicación cerrada normalmente por el usuario.")
        return 0

    except Exception as e:
        logger.critical(f"Excepción fatal no controlada: {e}", exc_info=True)
        try:
            # Ventana de diálogo emergente amigable para el operador
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error Inesperado",
                "Ocurrió un error inesperado al ejecutar la aplicación.\n\n"
                f"Detalle: {e}\n\n"
                "Consulte el archivo de registro en el directorio de logs para más detalles técnicos.",
            )
            root.destroy()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
