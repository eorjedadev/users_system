"""
MÓDULO REUTILIZABLE: app.controllers.document_controller

DESCRIPCIÓN:
    Controlador para la gestión del editor de documentos independiente.

RESPONSABILIDAD:
    - Gestionar las acciones de copiado al portapapeles, guardado a TXT y limpieza de texto.
    - Coordinar la inclusión opcional de los datos del usuario seleccionado al momento de copiar o guardar.
    - Garantizar que el editor de texto mantenga su independencia y no modifique el contenido
      escrito por el operador durante la combinación en memoria.

DEPENDENCIAS:
    - tkinter, tkinter.filedialog, tkinter.messagebox, pathlib.Path, typing.Callable
    - app.services.document_service (DocumentService)
    - app.controllers.user_controller (UserController)
    - app.views.main_window (MainWindow)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.controllers.main_controller
"""

from pathlib import Path
from tkinter import filedialog, messagebox

from app.controllers.user_controller import UserController
from app.services.document_service import DocumentService
from app.services.ticket_service import TicketService
from app.views.main_window import MainWindow
from app.utils.logger import get_logger

logger = get_logger("document_controller")


class DocumentController:
    """Controlador que gestiona la redacción, copiado, exportación de documentos TXT y registro de tickets."""

    def __init__(
        self,
        main_window: MainWindow,
        user_controller: UserController,
        ticket_service: Optional[TicketService] = None,
    ):
        self.main_window = main_window
        self.user_controller = user_controller
        self.ticket_service = ticket_service

        self._bind_events()

    def _bind_events(self) -> None:
        """Asigna los callbacks de la vista del documento."""
        self.main_window.document_view.on_copy = self.copy_document
        self.main_window.document_view.on_save_txt = self.save_document_txt
        self.main_window.document_view.on_clear = self.clear_document
        self.main_window.document_view.on_record_ticket = self.record_ticket

    def _prepare_export_content(self) -> str | None:
        """
        Prepara el contenido final a copiar o guardar respetando el estado de la casilla.
        Si la casilla está marcada pero no hay usuario seleccionado, advierte al operador.
        Retorna el contenido formateado o None si la operación debe cancelarse.
        """
        raw_text = self.main_window.document_view.get_document_text()
        include_user = self.main_window.document_view.is_include_user_checked()
        active_user = self.user_controller.get_current_user()

        if include_user and not active_user:
            proceed = messagebox.askyesno(
                "Sin Usuario Seleccionado",
                "Ha activado la opción 'Incluir los datos del usuario', pero no hay ningún usuario seleccionado en la ficha.\n\n"
                "¿Desea continuar procesando únicamente el texto del documento?",
                parent=self.main_window,
            )
            if not proceed:
                return None
            include_user = False

        if not raw_text.strip() and not (include_user and active_user):
            messagebox.showwarning("Documento Vacío", "No hay contenido para procesar. Escriba un texto en el editor.", parent=self.main_window)
            return None

        # Combinación en memoria: no altera el widget de texto original
        return DocumentService.combine_document(active_user, raw_text, include_user)

    def copy_document(self) -> None:
        """Copia el documento (o la combinación con usuario) al portapapeles de Windows."""
        content = self._prepare_export_content()
        if content is None:
            return

        success, msg = DocumentService.copy_to_clipboard(self.main_window, content)
        if success:
            messagebox.showinfo("Copiado Exitoso", "El documento ha sido copiado al portapapeles de Windows.", parent=self.main_window)
        else:
            messagebox.showerror("Error al Copiar", msg, parent=self.main_window)

    def save_document_txt(self) -> None:
        """Abre el diálogo de guardado y exporta el documento como archivo TXT con codificación UTF-8."""
        content = self._prepare_export_content()
        if content is None:
            return

        file_path_str = filedialog.asksaveasfilename(
            parent=self.main_window,
            title="Guardar documento como archivo TXT",
            defaultextension=".txt",
            filetypes=[("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos (*.*)", "*.*")],
        )
        if not file_path_str:
            return  # Operador canceló el diálogo

        target_path = Path(file_path_str)
        success, msg = DocumentService.save_to_txt_file(target_path, content)
        if success:
            messagebox.showinfo("Documento Guardado", msg, parent=self.main_window)
        else:
            messagebox.showerror("Error al Guardar", msg, parent=self.main_window)

    def clear_document(self) -> None:
        """Limpia el editor de texto tras confirmación previa del operador."""
        text = self.main_window.document_view.get_document_text()
        if not text.strip():
            return

        confirm = messagebox.askyesno(
            "Limpiar Editor",
            "¿Está seguro de que desea vaciar el contenido del editor de texto?",
            parent=self.main_window,
        )
        if confirm:
            self.main_window.document_view.clear_document()

    def record_ticket(self) -> None:
        """Registra el ticket de atención con el usuario seleccionado y el problema redactado."""
        if not self.ticket_service:
            from app.models.database import DatabaseManager
            self.ticket_service = TicketService(DatabaseManager())

        ticket_no = self.main_window.document_view.get_ticket_number()
        issue_detail = self.main_window.document_view.get_document_text()
        active_user = self.user_controller.get_current_user()

        if not ticket_no:
            messagebox.showwarning(
                "N° de Ticket Faltante",
                "Por favor, ingrese o pegue el número de ticket (ej: INC-10294) copiado de su ticketera.",
                parent=self.main_window,
            )
            return

        if not issue_detail and not active_user:
            messagebox.showwarning(
                "Datos Insuficientes",
                "Debe seleccionar un usuario o ingresar una descripción en el detalle del problema.",
                parent=self.main_window,
            )
            return

        ok, msg, ticket = self.ticket_service.record_ticket(ticket_no, active_user, issue_detail)
        if ok:
            user_label = ticket.user_full_name if ticket else "Usuario no especificado"
            messagebox.showinfo(
                "Ticket Registrado Exitosamente",
                f"El ticket #{ticket_no} se ha guardado correctamente en la base de datos local.\n\n"
                f"• Usuario: {user_label}\n"
                f"• Queda listo para incluirse en el reporte diario a tu jefatura.",
                parent=self.main_window,
            )
            # Limpiar campo de ticket y editor para la siguiente atención
            self.main_window.document_view.clear_ticket_number()
            self.main_window.document_view.clear_document()
        else:
            messagebox.showerror("Error al Registrar Ticket", msg, parent=self.main_window)
