# Sistema de Gestión de Usuarios, Documentación y Despacho Operativo

[![Desarrollador](https://img.shields.io/badge/Autor-Eduardo%20Orjeda%20Figueroa-blue.svg)](#autor-y-créditos)
[![Metodología](https://img.shields.io/badge/Metodología-AI--Augmented%20Software%20Engineering-orange.svg)](#metodología-de-desarrollo)
[![AI Partner](https://img.shields.io/badge/AI%20Engineering-Google%20Gemini-purple.svg)](#metodología-de-desarrollo)
[![Tests](https://img.shields.io/badge/Tests-31%20Passed%20(100%25)-brightgreen.svg)](#5-guía-para-desarrolladores-y-mantenimiento)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows%2010%20%7C%2011-0078D6.svg)](#1-características-principales)

Aplicación de escritorio profesional para entornos Windows desarrollada en **Python 3.11+**, **Tkinter/ttk** y **SQLite**, bajo una rigurosa arquitectura **MVC (Modelo-Vista-Controlador)** desacoplada y orientada a la alta productividad en centros de soporte técnico y operaciones.

El sistema permite gestionar de manera 100% local la información de más de 1.600 usuarios, redactar y exportar documentos, registrar tickets de atención diaria, generar reportes consolidados por turnos y despachar comunicaciones instantáneas a **WhatsApp Business Web** y **Microsoft Exchange / Outlook Web App (OWA)** corporativo.

> 📄 **Caso de Estudio y Memoria Técnica:**  
> Para consultar el análisis exhaustivo de arquitectura, patrones de diseño y decisiones de ingeniería de este proyecto, consulte el documento:  
> 🔗 **[docs/CASE_STUDY_ARQUITECTURA.md](docs/CASE_STUDY_ARQUITECTURA.md)**

---

## 1. Características Principales

* **Ejecutable Autónomo de Windows (`.exe`):** Se distribuye como un único archivo binario independiente (`dist/GestionUsuarios.exe`), sin requerir Python instalado en la máquina cliente ni consolas negras emergentes.
* **Persistencia Local Desatendida con SQLite (WAL Mode):** Autocreación de la base de datos `usuarios.db`, tablas, índices y migraciones en la primera ejecución. Configurado con `PRAGMA journal_mode = WAL` para alta concurrencia.
* **Cero Pérdida de Datos y Privacidad Total:** La base de datos y los registros se almacenan permanentemente en el directorio `%LOCALAPPDATA%` del usuario de Windows. Los datos, tickets y configuraciones de cada técnico permanecen 100% aislados en su propio equipo.
* **Registro de Tickets y Reporte Diario Consolidado:** Módulo para documentar atenciones técnicas en tiempo real y generar el reporte diario consolidado por turno, listo para despacho en un solo clic.
* **Despacho Multicanal Inteligente (WhatsApp y Exchange OWA):**
  - **Detección Dinámica de Navegadores:** Detecta si el técnico tiene sesiones activas en **Opera**, **Chrome** o **Edge** y despacha directamente a su navegador en uso.
  - **Mitigación del Límite de Microsoft Exchange:** Evasión del error HTTP 400 (`:-( Algo no fue bien`) en servidores IIS on-premise mediante inyección atómica del reporte al portapapeles (`Ctrl + V`).
* **Editor de Documentos Independiente:** Área multilínea con funciones de copiado al portapapeles y guardado en archivos TXT con codificación UTF-8.
* **Asistente de Importación CSV No Destructivo:** Inspección previa de codificación, detección de delimitador, respaldo atómico automático y carga masiva transaccional.

---

## 2. Ubicación de los Datos Persistentes en Windows

La aplicación centraliza todos sus datos en el almacenamiento local del perfil de usuario:

| Recurso | Ruta física en Windows |
|---|---|
| **Base de datos SQLite** | `%LOCALAPPDATA%\GestionUsuarios\data\usuarios.db`<br>*(ej: `C:\Users\<Usuario>\AppData\Local\GestionUsuarios\data\usuarios.db`)* |
| **Copias de seguridad** | `%LOCALAPPDATA%\GestionUsuarios\backups\` |
| **Archivos de registro (Logs)** | `%LOCALAPPDATA%\GestionUsuarios\logs\app.log` |

---

## 3. Instrucciones de Uso para el Operador

### A. Ejecución de la Aplicación
1. Ubique el archivo ejecutable en `dist/GestionUsuarios.exe` (o en su Escritorio).
2. Haga doble clic sobre `GestionUsuarios.exe`.
3. El programa detectará la base local (o la creará automáticamente si es la primera vez) y mostrará la interfaz lista para trabajar.

### B. Búsqueda y Selección de Usuarios
1. Ingrese cualquier término (nombre, login, RUT o teléfono) en la barra superior y presione **Enter** o haga clic en **🔍 Buscar**.
2. Si existen coincidencias, se listarán en la tabla central.
3. Haga clic sobre cualquier usuario de la tabla para cargar su ficha en el panel inferior.
4. Para quitar la selección activa, pulse **🧹 Limpiar selección**.

### C. Registro de Tickets y Reportes Diarios
1. Seleccione a un usuario y redacte las notas de atención en el editor.
2. Haga clic en **💾 Registrar Ticket**.
3. Al finalizar la jornada o turno, pulse **📊 Reporte Diario** para previsualizar el consolidado de atenciones, copiar el resumen o despacharlo a WhatsApp o Correo.

### D. Configuración de Entorno (Preferencias)
1. Pulse el botón **⚙️ Configuración** en la barra superior.
2. Seleccione su navegador preferido (*Automático*, *Opera*, *Chrome*, *Edge*).
3. Configure la URL corporativa de Outlook / Exchange Webmail si su empresa utiliza un servidor propio (por defecto preconfigurado para Entel: `https://correo.entelcc.cl/owa`).

---

## 4. Estructura del Código Fuente

```text
users_system/
├── app/
│   ├── controllers/       # MainController, UserController, DocumentController
│   ├── models/            # Entidades User, Ticket y DatabaseManager (SQLite WAL)
│   ├── services/          # UserService, TicketService, DispatchService, BackupService...
│   ├── views/             # MainWindow, estilos ttk modernos y modales modulares
│   └── utils/             # Paths seguros (AppData) y Logging rotativo
├── assets/                # Iconos del aplicativo (app_icon.ico, app_icon.png)
├── config/                # settings.py con constantes globales y esquema
├── docs/                  # Documentación técnica, CSVs y CASE_STUDY_ARQUITECTURA.md
├── scripts/               # build_exe.py (automatización de compilación con PyInstaller)
├── tests/                 # Suite de 31 pruebas unitarias e integradas automatizadas
├── main.py                # Punto de entrada principal
└── requirements.txt       # Dependencias del proyecto
```

---

## 5. Guía para Desarrolladores y Mantenimiento

### Comandos de Desarrollo
```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\activate

# 2. Ejecutar la aplicación desde código fuente
python main.py

# 3. Ejecutar la suite completa de 31 pruebas automatizadas
python tests/run_all_tests.py

# 4. Compilar el ejecutable Windows autónomo (.exe)
python scripts/build_exe.py
```

---

## 6. Metodología de Desarrollo

Este sistema fue desarrollado bajo el paradigma de **AI-Augmented Software Engineering (Ingeniería de Software Aumentada por IA)**:
* **Concepción & Dirección:** Eduardo Orjeda Figueroa diseñó la arquitectura, las reglas de negocio, los casos de uso operativos y los criterios de aceptación.
* **Prompt Engineering Avanzado:** Se utilizaron técnicas estructuradas de formulación de prompts con **Google Gemini (Plataforma Antigravity)**, incluyendo especificación de invariantes arquitectónicas, diseño orientado a pruebas, análisis de causas raíz de errores de red en Exchange IIS y refactorización continua.
* **Auditoría Humana de Calidad:** Cada componente, consulta SQL y flujo de interfaz fue probado, validado e integrado bajo estricto control de calidad.

---

## 7. Autor y Créditos

* **Desarrollador Principal:** **Eduardo Orjeda Figueroa**
* **Herramienta de Inteligencia Artificial:** **Google Gemini** (Antigravity Platform)
* **Licencia:** Propietario / Uso Comercial y Operativo Autorizado.
