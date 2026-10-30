# GymControl · MVP de gestión de gimnasio

Aplicación web para gestionar socios, membresías, control de acceso y métricas físicas de un gimnasio.
Proyecto del curso de Ingeniería de Software · Universidad Católica Luis Amigó · 2026.

**Equipo:** Sofía Carvajal Rivera · Valentina Marín Tuberquia
**Docente:** Daniel Felipe Agudelo Molina

## Funcionalidades

| Módulo | Historia | Rol |
| --- | --- | --- |
| Inicio de sesión por roles | RF-06 | Todos |
| Registrar socio | HU-01 | Recepcionista, Administrador |
| Validar acceso en recepción | HU-02 | Recepcionista, Administrador |
| Registrar métricas y calcular IMC | HU-03 | Entrenador, Administrador |
| Asignar / renovar membresía | HU-04 | Administrador |
| Registrar entrenador | HU-05 | Administrador |
| Consultar mi progreso | HU-06 | Socio |
| Reporte de morosos | HU-07 | Administrador |

## Inicio rápido

Requisitos: Python 3.10 o superior y Git.

```bash
git clone <url-del-repositorio>
cd gym-mvp
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
flask --app run seed --reset      # crea la base de datos y carga datos de demostración
python run.py                     # abre http://127.0.0.1:5000
```

### Usuarios de demostración

| Rol | Correo | Contraseña |
| --- | --- | --- |
| Administrador | admin@gimnasio.com | Admin2026* |
| Recepcionista | recepcion@gimnasio.com | Recepcion2026* |
| Entrenador | entrenador@gimnasio.com | Entrena2026* |
| Socio | andres.ramirez@correo.com | 1037000111 |

Documentos de prueba en recepción: `1037000111` (activa), `1037000222` (por vencer), `1037000333` (vencida).

## Pruebas

```bash
pytest -v --cov=app --html=reporte_pruebas.html --self-contained-html
```

45 casos (PU-01 a PU-14 y PI-01 a PI-11, derivados del plan de pruebas). Las evidencias de la última ejecución están en
[`docs/evidencias`](docs/evidencias).

## Estructura (arquitectura en capas MVC)

```
app/
├── models/          Modelo de dominio (diagrama de clases)
├── repositories.py  Acceso a datos
├── services/        Reglas de negocio de cada caso de uso
├── controllers/     Controladores (blueprints de Flask)
├── templates/       Vistas (Jinja2 + Bootstrap 5)
└── static/          CSS y librerías locales (funciona sin internet)
tests/               Pruebas unitarias e integración
docs/                Manuales, diagramas UML y evidencias
```

## Flujo de trabajo (Gitflow)

- `main`: versiones publicadas, etiquetadas `v0.1.0` … `v1.0.0`.
- `develop`: integración del sprint.
- `feature/HU-xx-descripcion`: una rama por historia de usuario.
- `release/x.y.0`: estabilización al cierre de cada sprint.
- `hotfix/x.y.z`: correcciones urgentes sobre `main`.

Mensajes de commit con [Conventional Commits](https://www.conventionalcommits.org/es/): `feat(HU-02): ...`, `fix(HU-03): ...`.

Más detalle en el [manual técnico](docs/MANUAL_TECNICO.md) y el [manual de usuario](docs/MANUAL_USUARIO.md).
