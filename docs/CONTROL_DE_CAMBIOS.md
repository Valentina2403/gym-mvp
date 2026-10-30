# Registro de solicitudes de cambio

Proceso definido en el Entregable 2 (sección 4.2): solicitud → análisis de impacto con la matriz de trazabilidad →
decisión del Product Owner → actualización del backlog → implementación en una rama `feature/` → verificación y cierre.

| ID | Solicitud | Origen | Impacto analizado | Decisión | Implementación |
| --- | --- | --- | --- | --- | --- |
| CC-01 | Permitir que el administrador restablezca la contraseña de un socio | Revisión del manual de usuario: un socio que olvide su clave no tenía cómo recuperarla | RF-06; controlador de socios; vista de detalle del socio; nueva prueba PI-11; manual de usuario | Aprobado para v1.0.0 | Rama `feature/CC-01-restablecer-contrasena`, fusionada en `develop` antes de `release/1.0.0` |
| CC-02 | Cambiar la tecnología de implementación de Java + Spring Boot a Python + Flask | Restricción del entorno de construcción: no había acceso a los repositorios de Maven | Arquitectura (sección 2.2 del Entregable 2) y tipos de datos del diagrama de clases. Las capas MVC, los casos de uso, las clases y las secuencias no cambian | Aprobado antes del Sprint 1 de construcción | Estructura equivalente: controladores = blueprints de Flask, servicios y repositorios en Python, SQLAlchemy en lugar de JPA, bcrypt en lugar de BCryptPasswordEncoder |
| CC-03 | El administrador hereda los permisos de Recepcionista y Entrenador | Rediseño del diagrama de casos de uso (generalización de actores) | RF-06; método `Cuenta.tiene_rol()`; pruebas PI-01c | Aprobado | Implementado desde v0.2.0 |

## Equivalencias de la arquitectura tras CC-02

| Diseño (Entregable 2) | Implementación (v1.0.0) |
| --- | --- |
| Spring MVC `@Controller` | Blueprints en `app/controllers/` |
| `@Service` + `@Transactional` | Clases en `app/services/` con `commit` / `rollback` explícitos |
| Spring Data JPA (repositorios) | `app/repositories.py` sobre SQLAlchemy |
| Entidades JPA | Modelos SQLAlchemy en `app/models/` |
| Thymeleaf + Bootstrap 5 | Jinja2 + Bootstrap 5 |
| Spring Security + BCryptPasswordEncoder | Flask-Login + decorador `rol_requerido` + bcrypt + CSRF de Flask-WTF |
| JUnit 5 + Mockito + MockMvc | pytest + `unittest.mock` + cliente de pruebas de Flask |
| MySQL 8 | SQLite en desarrollo, MySQL 8 en producción (misma cadena de conexión SQLAlchemy) |
