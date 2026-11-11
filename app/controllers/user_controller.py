"""
MÓDULO REUTILIZABLE: app.controllers.user_controller

DESCRIPCIÓN:
    Controlador para el flujo de gestión de usuarios (búsquedas, consultas y operaciones CRUD).

RESPONSABILIDAD:
    - Coordinar la interacción entre las vistas (SearchView, UserCardView, ActionsView, UserFormModal)
      y el servicio de persistencia (UserService).
    - Gestionar el usuario actualmente seleccionado en la sesión activa.
    - Manejar los diálogos modales de alta y modificación, preservando los datos si la validación falla.
    - Exigir confirmación explícita antes de guardar cambios o eliminar registros en SQLite.

DEPENDENCIAS:
    - tkinter, tkinter.messagebox, typing.Optional
    - app.models.user (User)
    - app.services.user_service (UserService)
    - app.views.main_window (MainWindow)
    - app.views.modals.user_form_modal (UserFormModal)
    - app.utils.logger (get_logger)

CONSUMIDORES:
    - app.controllers.main_controller
"""

from typing import Optional
from tkinter import messagebox

from app.models.user import User
from app.services.user_service import UserService
from app.views.main_window import MainWindow
from app.views.modals.user_form_modal import UserFormModal
from app.utils.logger import get_logger

logger = get_logger("user_controller")


class UserController:
    """Controlador que gestiona el ciclo de vida de los usuarios en la interfaz."""

    def __init__(self, main_window: MainWindow, user_service: UserService):
        self.main_window = main_window
        self.user_service = user_service
        self.current_user: Optional[User] = None

        self._bind_events()

    def _bind_events(self) -> None:
        """Asigna los callbacks de los componentes visuales a los métodos del controlador."""
        # SearchView
        self.main_window.search_view.on_search = self.search
        self.main_window.search_view.on_user_selected = self.select_user
        self.main_window.search_view.on_clear = self.clear_search

        # UserCardView
        self.main_window.user_card_view.on_clear_selection = self.clear_selection
        self.main_window.user_card_view.on_user_selected = self.select_user

        # ActionsView
        self.main_window.actions_view.on_add = self.open_add_modal
        self.main_window.actions_view.on_edit = self.open_edit_modal
        self.main_window.actions_view.on_delete = self.delete_current_user

    def get_current_user(self) -> Optional[User]:
        """Retorna el usuario actualmente seleccionado en la ficha."""
        return self.current_user

    def search(self, query: str = "") -> None:
        """Ejecuta una búsqueda y carga automáticamente los datos del usuario en la ficha."""
        query_clean = query.strip()
        if not query_clean:
            self.clear_selection()
            return

        try:
            results = self.user_service.search_users(query_clean)
            self.main_window.search_view.populate_results(results)
            logger.info(f"Búsqueda con término '{query_clean}' retornó {len(results)} resultados.")

            if results:
                # Carga inmediata del primer usuario encontrado en la ficha
                first_match = results[0]
                self.select_user(first_match.id)
                if len(results) > 1:
                    logger.info(f"Múltiples coincidencias ({len(results)}). Mostrando primero: {first_match.full_name}")
            else:
                messagebox.showinfo(
                    "Búsqueda de Usuario",
                    f"No se encontró ningún usuario con el criterio: '{query_clean}'.",
                    parent=self.main_window,
                )
                self.clear_selection()
        except Exception as e:
            logger.error(f"Error al ejecutar búsqueda: {e}", exc_info=True)
            messagebox.showerror("Error de Búsqueda", f"No se pudo consultar la base de datos:\n{e}", parent=self.main_window)

    def clear_search(self) -> None:
        """Restaura la búsqueda inicial y deselecciona cualquier usuario."""
        self.clear_selection()

    def select_user(self, user_id: int) -> None:
        """Carga un usuario en la ficha y habilita las acciones de edición y eliminación."""
        try:
            user = self.user_service.get_user_by_id(user_id)
            if user:
                self.current_user = user
                self.main_window.user_card_view.display_user(user)
                self.main_window.search_view.select_user_in_tree(user.id)
                self.main_window.actions_view.set_selection_state(True)
                self.main_window.status_bar_view.update_selected_user(user.full_name, user.id)
                logger.info(f"Usuario seleccionado: ID={user.id} ('{user.full_name}')")
            else:
                self.clear_selection()
        except Exception as e:
            logger.error(f"Error al seleccionar usuario ID={user_id}: {e}", exc_info=True)
            messagebox.showerror("Error de Consulta", f"No se pudo cargar el usuario:\n{e}", parent=self.main_window)

    def clear_selection(self) -> None:
        """Desmarca el usuario activo y bloquea las acciones dependientes."""
        self.current_user = None
        self.main_window.user_card_view.clear_card()
        self.main_window.search_view.clear_tree_selection()
        self.main_window.actions_view.set_selection_state(False)
        self.main_window.status_bar_view.update_selected_user(None, None)

    def open_add_modal(self) -> None:
        """Abre la ventana modal para registrar un nuevo usuario."""
        UserFormModal(
            parent=self.main_window,
            mode="add",
            user=None,
            on_save=self._handle_save_new_user,
        )

    def _handle_save_new_user(self, user_data: dict) -> bool:
        """Callback al confirmar el guardado de un nuevo usuario."""
        success, created_user, msg = self.user_service.create_user(user_data)
        if success and created_user:
            messagebox.showinfo("Usuario Agregado", msg, parent=self.main_window)
            self._refresh_views_after_change(select_user_id=created_user.id)
            return True
        else:
            messagebox.showwarning("Validación de Datos", msg, parent=self.main_window)
            return False

    def open_edit_modal(self) -> None:
        """Abre la ventana modal para editar el usuario seleccionado."""
        if not self.current_user:
            messagebox.showwarning("Sin Selección", "Debe seleccionar un usuario para poder editarlo.", parent=self.main_window)
            return

        UserFormModal(
            parent=self.main_window,
            mode="edit",
            user=self.current_user,
            on_save=self._handle_save_edited_user,
        )

    def _handle_save_edited_user(self, user_data: dict) -> bool:
        """Callback al confirmar cambios en la edición."""
        confirm = messagebox.askyesno(
            "Confirmar Guardado",
            f"¿Desea guardar los cambios para '{user_data.get('full_name')}'?",
            parent=self.main_window,
        )
        if not confirm:
            return False

        success, updated_user, msg = self.user_service.update_user(user_data)
        if success and updated_user:
            messagebox.showinfo("Usuario Actualizado", msg, parent=self.main_window)
            self._refresh_views_after_change(select_user_id=updated_user.id)
            return True
        else:
            messagebox.showwarning("Validación de Datos", msg, parent=self.main_window)
            return False

    def delete_current_user(self) -> None:
        """Solicita confirmación explícita y elimina el usuario seleccionado."""
        if not self.current_user:
            messagebox.showwarning("Sin Selección", "Debe seleccionar un usuario para eliminarlo.", parent=self.main_window)
            return

        # Confirmación con detalles de identidad según especificación CU-04
        user_identity = (
            f"• Nombre completo: {self.current_user.full_name}\n"
            f"• Usuario: {self.current_user.username or 'No registrado'}\n"
            f"• RUT: {self.current_user.rut or 'No registrado'}\n"
            f"• ID interno: #{self.current_user.id}"
        )

        confirm = messagebox.askyesno(
            "Confirmar Eliminación Definitiva",
            f"¿Está seguro de que desea eliminar permanentemente al usuario?\n\n{user_identity}\n\n"
            "Esta operación eliminará el registro de la base local y no se puede deshacer.",
            icon="warning",
            parent=self.main_window,
        )
        if not confirm:
            return

        success, msg = self.user_service.delete_user(self.current_user.id)
        if success:
            messagebox.showinfo("Eliminación Exitosa", msg, parent=self.main_window)
            self.clear_selection()
            self._refresh_views_after_change()
        else:
            messagebox.showerror("Error al Eliminar", msg, parent=self.main_window)

    def _refresh_views_after_change(self, select_user_id: Optional[int] = None) -> None:
        """Actualiza la tabla de búsqueda, el contador de la barra de estado y la selección."""
        current_query = self.main_window.search_view.get_query()
        self.search(current_query)

        total_count = self.user_service.get_total_count()
        self.main_window.status_bar_view.update_user_count(total_count)

        if select_user_id:
            self.select_user(select_user_id)
            self.main_window.search_view.select_user_in_tree(select_user_id)
