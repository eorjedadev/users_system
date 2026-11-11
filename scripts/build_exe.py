"""
PROYECTO: Sistema de Gestión de Usuarios, Documentación y Despacho Operativo
AUTOR: Eduardo Orjeda Figueroa | Lead Software Engineer & Prompt Engineer
METODOLOGÍA: AI-Augmented Software Engineering vía Google Gemini
MÓDULO: scripts.build_exe

DESCRIPCIÓN:
    Compila la aplicación en un ejecutable Windows autónomo (.exe) utilizando
    las opciones optimizadas para Tkinter y SQLite sin dependencias externas.
"""

from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import APP_NAME

PYINSTALLER_BIN = PROJECT_ROOT / ".venv" / "Scripts" / "pyinstaller.exe"
MAIN_SCRIPT = PROJECT_ROOT / "main.py"
ICON_PATH = PROJECT_ROOT / "assets" / "app_icon.ico"
ASSETS_DIR = PROJECT_ROOT / "assets"


def build_executable(onefile: bool = True) -> int:
    """Ejecuta PyInstaller con las opciones estándar de producción."""
    if not PYINSTALLER_BIN.exists():
        print(f"Error: No se encontró PyInstaller en {PYINSTALLER_BIN}")
        return 1

    # Limpiar build/ de forma tolerante a bloqueos transitorios
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir, ignore_errors=True)
        except Exception:
            pass

    cmd = [
        str(PYINSTALLER_BIN),
        "--noconsole",            # Sin ventana negra de consola (GUI pura)
        "--noconfirm",            # Sobrescribir dist/ previo sin preguntar
        "--name", APP_NAME,       # Nombre del ejecutable final
    ]

    if ICON_PATH.exists():
        cmd.extend(["--icon", str(ICON_PATH)])

    if ASSETS_DIR.exists():
        cmd.extend(["--add-data", f"{ASSETS_DIR};assets"])

    if onefile:
        cmd.append("--onefile")   # Un solo archivo .exe autónomo
    else:
        cmd.append("--onedir")    # Carpeta distribuible

    cmd.append(str(MAIN_SCRIPT))

    print(f"Iniciando compilación de {APP_NAME} (Onefile={onefile})...")
    print(f"Comando: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode == 0:
        exe_path = PROJECT_ROOT / "dist" / (f"{APP_NAME}.exe" if onefile else APP_NAME)
        # Asegurar copia de compatibilidad con nombre previo si correspondiera
        legacy_exe = PROJECT_ROOT / "dist" / "GestionUsuariosDocumentos.exe"
        if onefile and exe_path != legacy_exe:
            try:
                shutil.copy2(exe_path, legacy_exe)
                print(f"Copia de compatibilidad creada: {legacy_exe}")
            except Exception:
                pass

        print("\n==================================================")
        print("COMPILACIÓN COMPLETADA EXITOSAMENTE")
        print(f"Ubicación del ejecutable: {exe_path}")
        print("==================================================")
    else:
        print("\nError durante la compilación con PyInstaller.")

    return result.returncode


if __name__ == "__main__":
    is_onefile = "--onedir" not in sys.argv
    sys.exit(build_executable(onefile=is_onefile))
