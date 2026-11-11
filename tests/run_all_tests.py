from pathlib import Path
import sys
import unittest

# Asegurar que la raíz del proyecto esté en sys.path para importar app y config
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n==================================================")
        print("TODAS LAS PRUEBAS OBLIGATORIAS PASARON CON ÉXITO")
        print("==================================================")
        sys.exit(0)
    else:
        print("\n==================================================")
        print(f"FALLARON {len(result.failures) + len(result.errors)} PRUEBAS")
        print("==================================================")
        sys.exit(1)
