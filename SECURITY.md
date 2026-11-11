# Política de Seguridad y Protección de Datos (Security Policy)

## 1. Versiones Soportadas

Actualmente se proporciona soporte de seguridad y mantenimiento activo para las siguientes versiones:

| Versión | Soportada | Estado de Mantenimiento |
| :--- | :---: | :--- |
| `1.0.x` (LTS) | :white_check_mark: | Soporte activo y corrección de vulnerabilidades |
| `< 1.0.0` | :x: | Versiones de desarrollo preliminar (deprecadas) |

---

## 2. Principios de Seguridad y Privacidad por Diseño (Security by Design)

Este sistema fue concebido bajo el principio de **Privacidad y Aislamiento Local**:

1. **Cero Exposición a la Nube (Zero Cloud Exposure):**
   - El sistema opera de manera **100% local** en el sistema operativo Windows.
   - No transmite datos, credenciales ni reportes a servidores externos, APIs de terceros ni servicios de telemetría no autorizados.

2. **Aislamiento en `%LOCALAPPDATA%`:**
   - La base de datos SQLite (`usuarios.db`) reside en la ruta del perfil de usuario de Windows (`%LOCALAPPDATA%\GestionUsuarios\data\`).
   - Esto previene el acceso cruzado no autorizado entre usuarios que compartan la misma estación de trabajo física.

3. **Protección de Información Personal Identificable (PII):**
   - El archivo `.gitignore` del proyecto bloquea de forma predeterminada la subida de archivos CSV corporativos (`docs/data-*.csv`) para evitar cualquier fuga de datos de empleados o clientes (nombres, RUTs, teléfonos, correos).
   - Solo se incluye en el repositorio público una plantilla con datos anonimizados y de prueba (`docs/sample_users.csv`).

4. **Integración Segura con Navegadores y Exchange OWA:**
   - Para prevenir vulnerabilidades de inyección de comandos o URLs maliciosas, las URLs generadas hacia WhatsApp Web y Microsoft Exchange OWA son sanitizadas y codificadas con `urllib.parse.quote()`.
   - Se mitigan riesgos de desbordamiento de búfer o límites de petición en servidores Microsoft IIS transfiriendo cuerpos extensos a través del búfer del portapapeles del sistema operativo (`clipboard`).

---

## 3. Reporte Responsable de Vulnerabilidades (Vulnerability Disclosure)

Si descubres una posible vulnerabilidad de seguridad o un problema de exposición de datos en este proyecto, te solicitamos actuar con responsabilidad:

1. **NO abras un Issue público** en GitHub para reportar vulnerabilidades que puedan comprometer la seguridad de instalaciones activas.
2. Comunícate directamente y de forma privada con el autor y desarrollador principal:
   - **Responsable:** Eduardo Orjeda Figueroa
   - **Asunto del correo:** `[SEGURIDAD] Reporte de Vulnerabilidad - users_system`
3. Incluye en tu reporte:
   - Descripción detallada del hallazgo.
   - Pasos reproducibles o prueba de concepto (PoC).
   - Entorno donde se detectó (versión de Windows, versión de Python/ejecutable).
   - Impacto estimado.

Nos comprometemos a acusar recibo en un plazo inferior a 48 horas y proporcionar un plan de resolución o parche correctivo oportuno.

---
*Política de Seguridad mantenida por Eduardo Orjeda Figueroa.*
