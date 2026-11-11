"""
PROYECTO: Sistema de Gestión de Usuarios, Documentación y Despacho Operativo
AUTOR: Eduardo Orjeda Figueroa | Lead Software Engineer & Prompt Engineer
METODOLOGÍA: AI-Augmented Software Engineering vía Google Gemini
MÓDULO: app.controllers.main_controller

DESCRIPCIÓN:
    Controlador principal y coordinador de la arquitectura MVC de la aplicación.

RESPONSABILIDAD:
    - Instanciar e interconectar los modelos, servicios, vistas y subcontroladores.
    - Coordinar la apertura del Asistente de Importación CSV desde la cabecera.
    - Refrescar las vistas globales tras una importación masiva de datos.
    - Ejecutar la inicialización en el arranque y arrancar el ciclo de eventos (mainloop).

DEPENDENCIAS:
    - app.models.database (DatabaseManager)
    - app.services.user_service (UserService)
    - app.services.csv_service (CsvService, CsvImportSummary)
    - app.views.main_window (MainWindow)
    - app.views.modals.csv_import_modal (CsvImportModal)
    - app.controllers.user_controller (UserController)
    - app.controllers.document_controller (DocumentController)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - main
"""

from app.controllers.document_controller import DocumentController
from app.controllers.user_controller import UserController
from app.models.database import DatabaseManager
from app.services.csv_service import CsvImportSummary, CsvService
from app.services.settings_service import SettingsService
from app.services.ticket_service import TicketService
from app.services.user_service import UserService
from app.views.main_window import MainWindow
from app.views.modals.csv_import_modal import CsvImportModal
from app.views.modals.daily_report_modal import DailyReportModal
from app.views.modals.settings_modal import SettingsModal
from app.utils.logger import get_logger

logger = get_logger("main_controller")


class MainController:
    """Controlador central de la aplicación."""

    def __init__(self):
        logger.info("Inicializando MainController y subsistemas...")

        # 1. Capa de Persistencia y Modelos
        self.db_manager = DatabaseManager()

        # 2. Capa de Servicios de Negocio
        self.user_service = UserService(self.db_manager)
        self.csv_service = CsvService(self.db_manager)
        self.ticket_service = TicketService(self.db_manager)
        self.settings_service = SettingsService(self.db_manager)

        # 3. Capa de Vista Principal
        self.main_window = MainWindow()

        # 4. Capa de Controladores Especializados
        self.user_controller = UserController(self.main_window, self.user_service)
        self.document_controller = DocumentController(
            self.main_window,
            self.user_controller,
            self.ticket_service,
        )

        # 5. Enlace de acciones de cabecera
        self.main_window.header_view.on_import_csv = self.open_csv_import_modal
        self.main_window.header_view.on_daily_report = self.open_daily_report_modal
        self.main_window.header_view.on_settings = self.open_settings_modal

        # 6. Carga de estado inicial
        self._initialize_app_state()

    def _initialize_app_state(self) -> None:
        """Configura el estado inicial de la interfaz al abrir la aplicación."""
        db_name = self.db_manager.db_path.name
        self.main_window.status_bar_view.update_db_status(f"🟢 Base de datos: {db_name} (Conectada)")

        # Cargar total inicial y primera tanda de usuarios
        total_count = self.user_service.get_total_count()
        self.main_window.status_bar_view.update_user_count(total_count)

        initial_users = self.user_service.get_all_users(limit=100)
        self.main_window.search_view.populate_results(initial_users)
        self.main_window.user_card_view.update_user_list(initial_users)
        logger.info(f"Estado inicial cargado: {total_count} usuarios en base local.")

    def open_csv_import_modal(self) -> None:
        """Despliega la ventana modal del Asistente de Importación CSV."""
        CsvImportModal(
            parent=self.main_window,
            csv_service=self.csv_service,
            on_import_success=self._on_csv_imported,
        )

    def open_daily_report_modal(self) -> None:
        """Despliega la ventana modal del Reporte Diario de Tickets."""
        DailyReportModal(
            parent=self.main_window,
            ticket_service=self.ticket_service,
            settings_service=self.settings_service,
            on_open_settings_callback=self.open_settings_modal,
        )

    def open_settings_modal(self) -> None:
        """Despliega la ventana modal de Configuración de Destinatarios (Jefe y Encargado)."""
        SettingsModal(
            parent=self.main_window,
            settings_service=self.settings_service,
        )

    def _on_csv_imported(self, summary: CsvImportSummary) -> None:
        """Callback ejecutado tras completar con éxito una importación CSV."""
        logger.info(f"Actualizando interfaz tras importación de {summary.imported_count} registros.")
        total_count = self.user_service.get_total_count()
        self.main_window.status_bar_view.update_user_count(total_count)

        # Refrescar tabla de búsqueda
        self.user_controller.search("")

    def run(self) -> None:
        """Inicia el bucle principal de eventos de la aplicación."""
        logger.info("Iniciando mainloop de la aplicación...")
        self.main_window.mainloop()
