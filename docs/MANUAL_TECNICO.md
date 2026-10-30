# Manual técnico y de despliegue · GymControl v1.0.0

Este manual explica cómo instalar, configurar, ejecutar, probar y desplegar GymControl, el MVP de gestión de gimnasio.
Está dirigido a desarrolladores y a quien administre el servidor.

## 1. Resumen de la arquitectura

GymControl es una aplicación web monolítica en capas con patrón MVC, escrita en Python con Flask.

| Capa | Ubicación | Tecnología | Responsabilidad |
| --- | --- | --- | --- |
| Vista (V) | `app/templates/`, `app/static/` | Jinja2 + Bootstrap 5.3 (local) | Pantallas responsivas para PC, tableta y celular |
| Controlador (C) | `app/controllers/` | Blueprints de Flask | Reciben la petición, validan permisos por rol y eligen la vista |
| Servicios (M) | `app/services/` | Python | Reglas de negocio de cada caso de uso (CU-01 a CU-08) |
| Persistencia (M) | `app/repositories.py`, `app/models/` | SQLAlchemy 2 | Entidades del dominio y consultas |
| Seguridad | `app/controllers/decoradores.py`, `Cuenta` | Flask-Login, Flask-WTF, bcrypt | Sesión, permisos por rol, CSRF, contraseñas cifradas |
| Datos | `instance/gimnasio.db` o MySQL | SQLite 3 / MySQL 8 | Base de datos relacional |

![Arquitectura de alto nivel de GymControl](uml/arquitectura_flask.png)

Los diagramas UML del Entregable 2 están en `docs/uml/` (código fuente en `docs/uml/diagramas.puml`). El diseño original proponía Java + Spring Boot; la implementación usa Python + Flask con la misma arquitectura (solicitud de cambio CC-02, ver `docs/CONTROL_DE_CAMBIOS.md`).

## 2. Requisitos

| Componente | Versión mínima | Notas |
| --- | --- | --- |
| Python | 3.10 | Probado con 3.13; la integración continua usa 3.12 |
| pip | 23 | Viene con Python |
| Git | 2.30 | Para clonar el repositorio |
| Navegador | Chrome, Edge o Firefox recientes | La interfaz no requiere internet: Bootstrap y Chart.js van incluidos |
| MySQL (opcional) | 8.0 | Solo si no se usa SQLite |

### Dependencias de Python (`requirements.txt`)

| Paquete | Uso |
| --- | --- |
| Flask 3.1 | Framework web |
| Flask-SQLAlchemy 3.1 / SQLAlchemy 2.1 | Mapeo objeto-relacional |
| Flask-Login 0.6 | Sesión de usuario |
| Flask-WTF 1.3 | Protección CSRF en formularios |
| bcrypt 5.0 | Cifrado de contraseñas (RNF-03) |
| python-dotenv 1.2 | Lectura del archivo `.env` |
| PyMySQL 1.2 | Conector de MySQL (opcional) |
| gunicorn 23 | Servidor de producción en Linux |
| pytest, pytest-cov, pytest-html | Pruebas, cobertura y reporte |

## 3. Instalación en un equipo local

### Windows (PowerShell)

```powershell
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
flask --app run seed --reset
python run.py
```

Si PowerShell bloquea la activación del entorno, ejecuta una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### macOS / Linux

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run seed --reset
python run.py
```

La aplicación queda disponible en **http://127.0.0.1:5000**. Para abrirla desde una tableta en la misma red,
usa la IP del equipo, por ejemplo `http://192.168.1.20:5000`.

### Usuarios de demostración

| Rol | Correo | Contraseña |
| --- | --- | --- |
| Administrador | admin@gimnasio.com | Admin2026* |
| Recepcionista | recepcion@gimnasio.com | Recepcion2026* |
| Entrenador | entrenador@gimnasio.com | Entrena2026* |
| Socio | andres.ramirez@correo.com | 1037000111 |

Documentos para probar la recepción: `1037000111` (membresía activa), `1037000222` (por vencer),
`1037000333` (vencida) y cualquier número no registrado.

## 4. Configuración del entorno

La configuración se lee de variables de entorno o del archivo `.env` (plantilla en `.env.example`).

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `SECRET_KEY` | `cambie-esta-clave-en-produccion` | Firma las sesiones. **Cámbiala en producción** por un valor largo y aleatorio |
| `FLASK_ENV_NAME` | `development` | `development` o `production` |
| `DATABASE_URL` | SQLite en `instance/gimnasio.db` | Cadena de conexión de SQLAlchemy |
| `DIAS_AVISO_VENCIMIENTO` | `7` | Días antes del vencimiento en que la membresía pasa a "Por vencer" |

Para generar una clave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Usar MySQL en lugar de SQLite

1. Crea la base de datos y el usuario:
   ```sql
   CREATE DATABASE gimnasio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'gimnasio'@'localhost' IDENTIFIED BY 'clave-segura';
   GRANT ALL PRIVILEGES ON gimnasio.* TO 'gimnasio'@'localhost';
   ```
2. En `.env`: `DATABASE_URL=mysql+pymysql://gimnasio:clave-segura@localhost:3306/gimnasio`
3. Crea las tablas con `flask --app run init-db` (o `seed --reset` si quieres datos de demostración).

## 5. Comandos disponibles

| Comando | Qué hace |
| --- | --- |
| `python run.py` | Inicia el servidor de desarrollo en el puerto 5000 |
| `flask --app run init-db` | Crea las tablas vacías |
| `flask --app run seed --reset` | Borra todo y carga usuarios, planes y socios de demostración |
| `flask --app run actualizar-estados` | Recalcula el estado de todas las membresías (tarea diaria) |
| `pytest -v` | Ejecuta las 45 pruebas |

## 6. Modelo de datos

Las tablas corresponden al diagrama de clases del Entregable 2. `Persona` usa herencia de tabla única:
socios, empleados y entrenadores comparten la tabla `persona` y se distinguen por la columna `tipo`.

| Tabla | Contenido | Relaciones principales |
| --- | --- | --- |
| `persona` | Socios, empleados y entrenadores; `documento` único | — |
| `cuenta` | Usuario, hash bcrypt, rol, activa | 1 a 1 con `persona` |
| `especialidad` / `entrenador_especialidad` | Catálogo y asignación | N a N con entrenadores |
| `plan` | Mensual (30 días), Trimestral (90), Anual (365) | — |
| `membresia` | Fechas de inicio y fin, estado | N a 1 con socio y plan |
| `pago` | Monto, método, fecha, empleado que registra | 1 a 1 con membresía |
| `registro_acceso` | Fecha y hora, resultado, motivo | N a 1 con socio y empleado |
| `medicion_fisica` | Peso, altura, % de grasa (opcional), IMC | N a 1 con socio y empleado |

Reglas implementadas en el modelo:

- `Membresia.esta_vigente(fecha)`: vigente desde la fecha de inicio hasta la de fin, inclusive.
- `Membresia.actualizar_estado(fecha)`: transiciones del diagrama de estados (Activa → Por vencer → Vencida).
- `MedicionFisica.calcular_imc()`: peso / altura², redondeado a 2 decimales.
- `Cuenta.tiene_rol()`: el administrador hereda los permisos de recepción y entrenamiento.

## 7. Permisos por rol

| Ruta | Administrador | Recepcionista | Entrenador | Socio |
| --- | :---: | :---: | :---: | :---: |
| `/` Inicio | Sí | Sí | Sí | Redirige a Mi progreso |
| `/acceso/` Validar acceso | Sí | Sí | No | No |
| `/socios/` Listado y detalle | Sí | Sí | Sí | No |
| `/socios/nuevo` Registrar socio | Sí | Sí | No | No |
| `/socios/<id>/renovar` | Sí | No | No | No |
| `/socios/<id>/metricas` | Sí | No | Sí | No |
| `/socios/<id>/restablecer-contrasena` | Sí | No | No | No |
| `/entrenadores/` | Sí | No | No | No |
| `/reportes/` | Sí | No | No | No |
| `/mi-progreso` | No | No | No | Sí |

Una ruta no permitida responde **403** con una página explicativa.

## 8. Pruebas

```bash
pytest -v --cov=app --cov-report=html --html=reporte_pruebas.html --self-contained-html
```

- **45 casos** que implementan el plan de pruebas del Entregable 2: PU-01 a PU-14 (unitarias, `tests/unit/`) y
  PI-01 a PI-10 (integración, `tests/integration/`), más PI-11 para el restablecimiento de contraseñas.
- Las pruebas usan una base SQLite en memoria; no tocan los datos reales.
- Cobertura actual: **84 %** del código (meta: 70 %).
- La prueba PI-08 mide el RNF-01 con 1.003 socios cargados: percentil 95 de **22 ms** frente al límite de 2 s.
- GitHub Actions (`.github/workflows/pruebas.yml`) ejecuta todo en cada *push* y *pull request* y bloquea
  la fusión si la cobertura baja de 70 %.

Las evidencias de la última ejecución están en `docs/evidencias/`.

## 9. Despliegue en producción (Linux)

Pasos para un servidor Ubuntu 22.04 o superior:

1. Instala dependencias del sistema: `sudo apt install python3-venv nginx git`.
2. Clona el repositorio en `/opt/gymcontrol`, crea el entorno virtual e instala `requirements.txt`.
3. Crea `/opt/gymcontrol/.env` con `FLASK_ENV_NAME=production`, una `SECRET_KEY` nueva y `DATABASE_URL` de MySQL.
4. Crea las tablas: `flask --app run init-db`. Crea el primer administrador con `flask --app run seed --reset`
   y cambia su contraseña desde **Mi cuenta**, o carga los usuarios reales manualmente.
5. Crea el servicio `/etc/systemd/system/gymcontrol.service`:
   ```ini
   [Unit]
   Description=GymControl
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/opt/gymcontrol
   EnvironmentFile=/opt/gymcontrol/.env
   ExecStart=/opt/gymcontrol/.venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 run:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   Actívalo: `sudo systemctl enable --now gymcontrol`.
6. Configura Nginx como proxy inverso hacia `127.0.0.1:8000` y habilita HTTPS con Certbot.
7. Programa la tarea diaria de estados con `crontab -e`:
   ```
   5 0 * * * cd /opt/gymcontrol && .venv/bin/flask --app run actualizar-estados
   ```
   En Windows se usa el Programador de tareas con el mismo comando.

**Respaldo.** Con SQLite basta copiar `instance/gimnasio.db` con el servicio detenido. Con MySQL:
`mysqldump gimnasio > respaldo_$(date +%F).sql`, programado a diario.

## 10. Control de versiones

El repositorio sigue **Gitflow**:

| Rama | Uso |
| --- | --- |
| `main` | Versiones publicadas, con etiquetas `v0.1.0`, `v0.2.0`, `v0.3.0`, `v1.0.0` |
| `develop` | Integración del sprint en curso |
| `feature/HU-xx-descripcion` | Una rama por historia de usuario |
| `release/x.y.0` | Estabilización al cierre de cada sprint |
| `hotfix/x.y.z` | Correcciones urgentes sobre `main` |

Los mensajes de commit siguen *Conventional Commits* con la historia de usuario: `feat(HU-02): ...`, `fix(HU-03): ...`,
`test: ...`, `docs: ...`. Los cambios de cada versión están en `CHANGELOG.md` y las solicitudes de cambio en `docs/CONTROL_DE_CAMBIOS.md`.

Para ver el historial: `git log --oneline --graph --all`.

## 11. Solución de problemas

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| `flask: command not found` | El entorno virtual no está activo | Actívalo (paso 3) o usa `python -m flask --app run ...` |
| `no such table: cuenta` | La base de datos no se ha creado | `flask --app run seed --reset` |
| La página carga sin estilos | Se abrió el HTML directamente | Abre la aplicación desde `http://127.0.0.1:5000` |
| "The CSRF token is missing" | La sesión expiró o se cambió `SECRET_KEY` | Recarga la página e inicia sesión de nuevo |
| El puerto 5000 está ocupado | Otra aplicación lo usa (en macOS, AirPlay) | Cambia el puerto en `run.py` o desactiva AirPlay Receiver |
| La tableta no abre la aplicación | El firewall bloquea el puerto | Permite Python en el firewall y usa la IP del equipo |
