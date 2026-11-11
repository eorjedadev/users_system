"""
MÓDULO REUTILIZABLE: app.views.styles

DESCRIPCIÓN:
    Configuración global de temas, fuentes y paleta cromática profesional para ttk.Style.

RESPONSABILIDAD:
    - Aplicar una estética ejecutiva, limpia y de alto contraste basada en el tema 'clam'.
    - Eliminar bordes toscos o anticuados y aplicar espaciados proporcionados.
    - Definir colores modernos: Slate oscuro, azul cobalto, grises suaves y blancos puros.

DEPENDENCIAS:
    - tkinter, tkinter.ttk
"""

import tkinter as tk
from tkinter import ttk

import tkinter as tk
from tkinter import ttk

# Paleta cromática corporativa ejecutiva (Fiel a la maqueta de referencia)
COLOR_HEADER_BG = "#0b2545"        # Navy corporativo oscuro elegante
COLOR_HEADER_TITLE = "#ffffff"     # Blanco puro
COLOR_HEADER_SUBTITLE = "#94a3b8"  # Slate suave 400

COLOR_BG_WINDOW = "#eef4f9"        # Fondo general de la ventana (gris azulado hielo)
COLOR_BG_CARD = "#ffffff"          # Blanco puro de tarjetas
COLOR_BORDER_CARD = "#dbe5ef"      # Borde sutil de tarjetas
COLOR_FIELD_BG = "#f0f4f8"         # Fondo suave celeste/gris de los campos de entrada
COLOR_FIELD_BORDER = "#cbd5e1"     # Borde de campos

COLOR_TEXT_MAIN = "#0f172a"        # Texto principal oscuro de alto contraste
COLOR_TEXT_NAVY = "#0b2545"        # Títulos navy de tarjetas y secciones
COLOR_TEXT_LABEL = "#1e293b"       # Etiquetas de campos
COLOR_TEXT_MUTED = "#64748b"       # Textos secundarios y placeholders

# Botones temáticos
COLOR_BTN_ADD_BG = "#16a34a"       # Verde vibrante
COLOR_BTN_ADD_HOVER = "#15803d"
COLOR_BTN_ADD_FG = "#ffffff"

COLOR_BTN_EDIT_BG = "#eff6ff"      # Azul claro pastel
COLOR_BTN_EDIT_BORDER = "#93c5fd"  # Borde azul claro
COLOR_BTN_EDIT_FG = "#2563eb"      # Azul cobalto
COLOR_BTN_EDIT_HOVER = "#dbeafe"

COLOR_BTN_DELETE_BG = "#fef2f2"    # Rojo claro pastel
COLOR_BTN_DELETE_BORDER = "#fca5a5"# Borde rojo suave
COLOR_BTN_DELETE_FG = "#dc2626"    # Rojo carmesí
COLOR_BTN_DELETE_HOVER = "#fee2e2"

COLOR_BTN_SAVE_BG = "#eff6ff"      # Azul claro de Guardar TXT
COLOR_BTN_SAVE_BORDER = "#93c5fd"
COLOR_BTN_SAVE_FG = "#2563eb"
COLOR_BTN_SAVE_HOVER = "#dbeafe"

COLOR_BTN_OUTLINE_BG = "#ffffff"   # Botón contorno blanco
COLOR_BTN_OUTLINE_BORDER = "#cbd5e1"
COLOR_BTN_OUTLINE_FG = "#1e293b"
COLOR_BTN_OUTLINE_HOVER = "#f1f5f9"

COLOR_STATUS_BG = "#e9f2fa"        # Fondo de barra de estado
COLOR_STATUS_DB = "#0369a1"        # Azul conexión SQLite
COLOR_STATUS_TEXT = "#475569"      # Gris texto de conteos

# Tipografías Segoe UI (Estándar Windows moderno)
FONT_FAMILY = "Segoe UI"
FONT_HEADER_TITLE = (FONT_FAMILY, 12, "bold")
FONT_HEADER_SUB = (FONT_FAMILY, 8, "normal")
FONT_CARD_TITLE = (FONT_FAMILY, 10, "bold")
FONT_SEARCH_TITLE = (FONT_FAMILY, 9, "bold")
FONT_FIELD_LABEL = (FONT_FAMILY, 8, "bold")
FONT_FIELD_VALUE = (FONT_FAMILY, 9, "normal")
FONT_BTN_ACTION = (FONT_FAMILY, 9, "bold")
FONT_BTN_REGULAR = (FONT_FAMILY, 8, "bold")
FONT_HINT = (FONT_FAMILY, 8, "normal")
FONT_STATUS = (FONT_FAMILY, 8, "normal")


def configure_app_styles(root: tk.Tk) -> ttk.Style:
    """Configura y aplica estilos modernos de alto impacto visual para toda la app."""
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=COLOR_BG_WINDOW)

    # 1. Marcos base y fondos
    style.configure("TFrame", background=COLOR_BG_WINDOW)
    style.configure("Header.TFrame", background=COLOR_HEADER_BG)
    style.configure("Card.TFrame", background=COLOR_BG_CARD)
    style.configure("Status.TFrame", background=COLOR_STATUS_BG)

    # 2. Etiquetas base y títulos
    style.configure("TLabel", background=COLOR_BG_WINDOW, foreground=COLOR_TEXT_MAIN, font=FONT_FIELD_VALUE)
    style.configure("Card.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT_MAIN, font=FONT_FIELD_VALUE)
    style.configure("CardTitle.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT_NAVY, font=FONT_CARD_TITLE)
    style.configure("SearchTitle.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT_NAVY, font=FONT_SEARCH_TITLE)
    style.configure("FieldLabel.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT_LABEL, font=FONT_FIELD_LABEL)
    style.configure("Hint.TLabel", background=COLOR_BG_CARD, foreground="#0284c7", font=FONT_HINT)

    # Cabecera
    style.configure("HeaderTitle.TLabel", background=COLOR_HEADER_BG, foreground=COLOR_HEADER_TITLE, font=FONT_HEADER_TITLE)
    style.configure("HeaderSubtitle.TLabel", background=COLOR_HEADER_BG, foreground=COLOR_HEADER_SUBTITLE, font=FONT_HEADER_SUB)

    # Barra de estado
    style.configure("StatusDb.TLabel", background=COLOR_STATUS_BG, foreground=COLOR_STATUS_DB, font=FONT_STATUS)
    style.configure("StatusText.TLabel", background=COLOR_STATUS_BG, foreground=COLOR_STATUS_TEXT, font=FONT_STATUS)

    # 3. Botón de Cabecera (Importar CSV)
    style.configure(
        "HeaderImport.TButton",
        background=COLOR_HEADER_BG,
        foreground="#ffffff",
        font=FONT_BTN_REGULAR,
        borderwidth=1,
        bordercolor="#64748b",
        focuscolor="none",
        padding=(10, 4),
    )
    style.map(
        "HeaderImport.TButton",
        background=[("pressed", "#1e3a5f"), ("active", "#153359"), ("disabled", COLOR_HEADER_BG)],
        foreground=[("disabled", "#64748b")],
        bordercolor=[("active", "#94a3b8")],
    )

    # 4. Botones de Tarjeta de Acciones
    # [ ＋ Agregar usuario ] - Verde vibrante sólido
    style.configure(
        "AddUser.TButton",
        background=COLOR_BTN_ADD_BG,
        foreground=COLOR_BTN_ADD_FG,
        font=FONT_BTN_ACTION,
        borderwidth=0,
        focuscolor="none",
        padding=(10, 6),
    )
    style.map(
        "AddUser.TButton",
        background=[("pressed", "#14532d"), ("active", COLOR_BTN_ADD_HOVER), ("disabled", "#94a3b8")],
        foreground=[("disabled", "#f8fafc")],
    )

    # [ ✎ Editar usuario ] - Pastel celeste con borde azul
    style.configure(
        "EditUser.TButton",
        background=COLOR_BTN_EDIT_BG,
        foreground=COLOR_BTN_EDIT_FG,
        font=FONT_BTN_ACTION,
        borderwidth=1,
        bordercolor=COLOR_BTN_EDIT_BORDER,
        focuscolor="none",
        padding=(10, 6),
    )
    style.map(
        "EditUser.TButton",
        background=[("pressed", "#bfdbfe"), ("active", COLOR_BTN_EDIT_HOVER), ("disabled", "#f1f5f9")],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("disabled", "#e2e8f0")],
    )

    # [ 🗑 Eliminar usuario ] - Pastel rojo con borde rojo suave
    style.configure(
        "DeleteUser.TButton",
        background=COLOR_BTN_DELETE_BG,
        foreground=COLOR_BTN_DELETE_FG,
        font=FONT_BTN_ACTION,
        borderwidth=1,
        bordercolor=COLOR_BTN_DELETE_BORDER,
        focuscolor="none",
        padding=(10, 6),
    )
    style.map(
        "DeleteUser.TButton",
        background=[("pressed", "#fecaca"), ("active", COLOR_BTN_DELETE_HOVER), ("disabled", "#f1f5f9")],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("disabled", "#e2e8f0")],
    )

    # 5. Botones de Documento y Limpieza
    # [ 📥 Guardar TXT ] - Azul claro con borde azul
    style.configure(
        "SaveDoc.TButton",
        background=COLOR_BTN_SAVE_BG,
        foreground=COLOR_BTN_SAVE_FG,
        font=FONT_BTN_REGULAR,
        borderwidth=1,
        bordercolor=COLOR_BTN_SAVE_BORDER,
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "SaveDoc.TButton",
        background=[("pressed", "#bfdbfe"), ("active", COLOR_BTN_SAVE_HOVER), ("disabled", "#f1f5f9")],
        foreground=[("disabled", "#94a3b8")],
    )

    # Botones contorno blanco ([ 📋 Copiar texto ], [ 🧹 Limpiar documento ], [ 🔄 Limpiar selección ])
    style.configure(
        "Outline.TButton",
        background=COLOR_BTN_OUTLINE_BG,
        foreground=COLOR_BTN_OUTLINE_FG,
        font=FONT_BTN_REGULAR,
        borderwidth=1,
        bordercolor=COLOR_BTN_OUTLINE_BORDER,
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "Outline.TButton",
        background=[("pressed", "#e2e8f0"), ("active", COLOR_BTN_OUTLINE_HOVER), ("disabled", "#f8fafc")],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("disabled", "#e2e8f0")],
    )

    # Botones de la barra de búsqueda (Iconos Buscar y Actualizar)
    style.configure(
        "SearchIcon.TButton",
        background="#2563eb",
        foreground="#ffffff",
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=0,
        focuscolor="none",
        padding=(6, 3),
    )
    style.map(
        "SearchIcon.TButton",
        background=[("pressed", "#1e40af"), ("active", "#1d4ed8"), ("disabled", "#94a3b8")],
        foreground=[("disabled", "#f8fafc")],
    )

    style.configure(
        "RefreshIcon.TButton",
        background="#ffffff",
        foreground="#1e293b",
        font=(FONT_FAMILY, 10, "bold"),
        borderwidth=1,
        bordercolor="#cbd5e1",
        focuscolor="none",
        padding=(6, 3),
    )
    style.map(
        "RefreshIcon.TButton",
        background=[("pressed", "#e2e8f0"), ("active", "#f1f5f9"), ("disabled", "#f8fafc")],
        foreground=[("disabled", "#94a3b8")],
    )

    # Botón Principal Sólido ([ 💾 Registrar Ticket ], [ 💾 Guardar ], [ 📥 Iniciar Importación ])
    style.configure(
        "Primary.TButton",
        background="#2563eb",
        foreground="#ffffff",
        font=FONT_BTN_REGULAR,
        borderwidth=0,
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "Primary.TButton",
        background=[("pressed", "#1e40af"), ("active", "#1d4ed8"), ("disabled", "#94a3b8")],
        foreground=[("disabled", "#f8fafc")],
    )

    # Botón de Acción / Secundario Contorno ([ ✕ Cancelar ], [ ✕ Cerrar ], [ 📁 Examinar... ])
    style.configure(
        "Action.TButton",
        background="#ffffff",
        foreground="#334155",
        font=FONT_BTN_REGULAR,
        borderwidth=1,
        bordercolor="#cbd5e1",
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "Action.TButton",
        background=[("pressed", "#e2e8f0"), ("active", "#f1f5f9"), ("disabled", "#f8fafc")],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("disabled", "#e2e8f0")],
    )

    # Botón Despacho Outlook ([ 📧 Abrir en Outlook ])
    style.configure(
        "Outlook.TButton",
        background="#eff6ff",
        foreground="#0078d4",
        font=FONT_BTN_REGULAR,
        borderwidth=1,
        bordercolor="#93c5fd",
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "Outlook.TButton",
        background=[("pressed", "#bfdbfe"), ("active", "#dbeafe"), ("disabled", "#f1f5f9")],
        foreground=[("disabled", "#94a3b8")],
    )

    # Botón WhatsApp Primario ([ 💬 WhatsApp Jefe ])
    style.configure(
        "WhatsApp.TButton",
        background="#16a34a",
        foreground="#ffffff",
        font=FONT_BTN_REGULAR,
        borderwidth=0,
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "WhatsApp.TButton",
        background=[("pressed", "#14532d"), ("active", "#15803d"), ("disabled", "#94a3b8")],
        foreground=[("disabled", "#f8fafc")],
    )

    # Botón WhatsApp Secundario ([ 💬 WhatsApp Encargado ])
    style.configure(
        "WhatsAppOutline.TButton",
        background="#f0fdf4",
        foreground="#15803d",
        font=FONT_BTN_REGULAR,
        borderwidth=1,
        bordercolor="#86efac",
        focuscolor="none",
        padding=(8, 4),
    )
    style.map(
        "WhatsAppOutline.TButton",
        background=[("pressed", "#bbf7d0"), ("active", "#dcfce7"), ("disabled", "#f1f5f9")],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("disabled", "#e2e8f0")],
    )

    # Estilos de LabelFrame para modales limpios sin bordes grises anticuados
    style.configure("TLabelframe", background="#f8fafc", bordercolor="#cbd5e1", borderwidth=1)
    style.configure("TLabelframe.Label", background="#f8fafc", foreground="#0b2545", font=("Segoe UI", 9, "bold"))

    # 6. Entradas de Texto estilizadas con fondo suave #f0f4f8
    style.configure(
        "Soft.TEntry",
        fieldbackground=COLOR_FIELD_BG,
        foreground=COLOR_TEXT_MAIN,
        bordercolor=COLOR_FIELD_BORDER,
        padding=(4, 3),
    )
    style.configure(
        "TEntry",
        fieldbackground=COLOR_FIELD_BG,
        foreground=COLOR_TEXT_MAIN,
        bordercolor=COLOR_FIELD_BORDER,
        padding=(4, 3),
    )

    # 7. Combobox estilizado
    style.configure(
        "Search.TCombobox",
        fieldbackground="#ffffff",
        background="#ffffff",
        foreground=COLOR_TEXT_MAIN,
        bordercolor=COLOR_FIELD_BORDER,
        arrowcolor=COLOR_TEXT_NAVY,
        padding=4,
    )

    # 8. Casilla de verificación
    style.configure(
        "TCheckbutton",
        background=COLOR_BG_CARD,
        foreground="#475569",
        font=FONT_HINT,
    )
    style.map("TCheckbutton", background=[("active", COLOR_BG_CARD)])

    return style

