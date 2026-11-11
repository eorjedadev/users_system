"""
MÓDULO REUTILIZABLE: app.views.modals.csv_import_modal

DESCRIPCIÓN:
    Ventana modal para el Asistente de Importación y Validación previa de archivos CSV.

RESPONSABILIDAD:
    - Permitir seleccionar un archivo CSV desde cualquier ubicación del sistema.
    - Mostrar inspección previa (codificación, delimitador, columnas mapeadas, total de registros).
    - Solicitar confirmación explícita del operador antes de ejecutar la importación en SQLite.
    - Desplegar el resumen final con la cantidad de registros importados y advertencias.

DEPENDENCIAS:
    - tkinter, tkinter.ttk, tkinter.filedialog, tkinter.messagebox, pathlib.Path, typing.Callable, typing.Optional
    - app.services.csv_service (CsvService, CsvInspectionResult, CsvImportSummary)
"""

from pathlib import Path
from typing import Callable, Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.services.csv_service import CsvInspectionResult, CsvImportSummary, CsvService
from app.utils.window_utils import apply_app_icon


class CsvImportModal(tk.Toplevel):
    """Diálogo modal para el Asistente de Importación de archivos CSV."""

    def __init__(
        self,
        parent: tk.Misc,
        csv_service: CsvService,
        on_import_success: Optional[Callable[[CsvImportSummary], None]] = None,
    ):
        super().__init__(parent)
        self.csv_service = csv_service
        self.on_import_success = on_import_success
        self.current_inspection: Optional[CsvInspectionResult] = None

        self.title("Asistente de Importación CSV")
        self.minsize(560, 440)
        self.resizable(True, True)
        self.configure(bg="#f8fafc")
        apply_app_icon(self)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_window(parent)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # 1. Botones inferiores fijados SIEMPRE abajo (side='bottom') para evitar recortes
        btn_box = ttk.Frame(container)
        btn_box.pack(side="bottom", fill="x", pady=(12, 0))

        btn_cancel = ttk.Button(btn_box, text="✕  Cancelar", style="Action.TButton", command=self.destroy, cursor="hand2")
        btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_import = ttk.Button(
            btn_box,
            text="📥  Iniciar Importación",
            style="Primary.TButton",
            command=self._execute_import,
            state="disabled",
            cursor="hand2",
        )
        self.btn_import.pack(side="right")

        # 2. Selector de archivo CSV (arriba)
        file_frame = ttk.LabelFrame(container, text="  Selección de archivo CSV  ", padding=12)
        file_frame.pack(side="top", fill="x", pady=(0, 12))

        self.var_filepath = tk.StringVar()
        self.entry_file = ttk.Entry(file_frame, textvariable=self.var_filepath, width=50, font=("Segoe UI", 9))
        self.entry_file.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = ttk.Button(file_frame, text="📁  Examinar...", style="Action.TButton", command=self._browse_file, cursor="hand2")
        btn_browse.pack(side="right")

        # 3. Panel de Inspección Preliminar (toma todo el espacio restante)
        self.inspect_frame = ttk.LabelFrame(container, text="  Diagnóstico y Mapeo Detectado  ", padding=12)
        self.inspect_frame.pack(side="top", fill="both", expand=True)

        self.lbl_info = ttk.Label(
            self.inspect_frame,
            text="Seleccione un archivo CSV para inspeccionar su estructura y codificación.",
            foreground="#64748b",
            wraplength=520,
            justify="left",
            font=("Segoe UI", 9),
        )
        self.lbl_info.pack(fill="both", expand=True, pady=4)

    def _browse_file(self) -> None:
        file_path_str = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo CSV para importar",
            filetypes=[("Archivos CSV (*.csv)", "*.csv"), ("Todos los archivos (*.*)", "*.*")],
        )
        if not file_path_str:
            return

        path = Path(file_path_str)
        self.var_filepath.set(str(path))
        self._inspect_file(path)

    def _inspect_file(self, path: Path) -> None:
        try:
            inspection = self.csv_service.inspect_csv(path)
            self.current_inspection = inspection

            info_text = (
                f"• Archivo: {path.name}\n"
                f"• Codificación detectada: {inspection.encoding.upper()}\n"
                f"• Delimitador de campos: '{inspection.delimiter}'\n"
                f"• Total de registros detectados: {inspection.total_rows:,}\n\n"
                f"• Columnas mapeadas ({len(inspection.proposed_mapping)}/7):\n"
                f"   {', '.join(f'{k} -> {v}' for k, v in inspection.proposed_mapping.items())}\n"
            )
            if inspection.unmapped_columns:
                info_text += f"\n• Columnas omitidas (no requeridas): {', '.join(inspection.unmapped_columns)}"

            self.lbl_info.configure(text=info_text, foreground="#0f172a")

            if "full_name" in inspection.proposed_mapping:
                self.btn_import.configure(state="normal")
            else:
                self.btn_import.configure(state="disabled")
                messagebox.showwarning(
                    "Columna Faltante",
                    "El archivo no contiene una columna reconocible para 'Nombre Completo'.",
                    parent=self,
                )
        except Exception as e:
            self.lbl_info.configure(text=f"Error al inspeccionar archivo: {e}", foreground="#dc2626")
            self.btn_import.configure(state="disabled")

    def _execute_import(self) -> None:
        if not self.current_inspection:
            return

        confirm = messagebox.askyesno(
            "Confirmar Importación Masiva",
            f"¿Desea importar {self.current_inspection.total_rows:,} registros desde '{self.current_inspection.filepath.name}'?\n\n"
            "Se creará automáticamente una copia de seguridad previa de la base de datos.",
            parent=self,
        )
        if not confirm:
            return

        try:
            summary = self.csv_service.import_csv_data(
                self.current_inspection.filepath,
                self.current_inspection.proposed_mapping,
            )

            msg = (
                f"Importación completada con éxito.\n\n"
                f"• Registros leídos: {summary.total_read:,}\n"
                f"• Registros importados: {summary.imported_count:,}\n"
                f"• Registros omitidos (sin nombre): {summary.skipped_count}\n"
            )
            if summary.backup_path:
                msg += f"\nCopia de seguridad guardada en:\n{summary.backup_path.name}"

            messagebox.showinfo("Importación Exitosa", msg, parent=self)

            if self.on_import_success:
                self.on_import_success(summary)
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Error en la Importación",
                f"Ocurrió un error al procesar el archivo CSV:\n{e}",
                parent=self,
            )

    def _center_window(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        w = 600
        h = 470
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
