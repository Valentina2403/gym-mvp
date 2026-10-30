# Registro de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado semántico.

## [0.3.0] — Sprint 3
### Agregado
- Validación de acceso en recepción con alertas verde, ámbar y roja (HU-02, RF-03).
- Asignación y renovación de membresías con registro de pago manual (HU-04, RF-02).
- Registro de métricas físicas y cálculo automático del IMC (HU-03, RF-04).
- Historial de progreso del socio con gráfica de peso (HU-06, RF-08).
- Cancelación de membresías y comando diario `actualizar-estados`.

## [0.2.0] — Sprint 2
### Agregado
- Inicio de sesión con roles y contraseñas cifradas con bcrypt (RF-06, RNF-03).
- Panel de inicio con indicadores.
- Datos de demostración (`flask --app run seed --reset`).
- Registro y listado de socios con validación de documento único (HU-01, RF-01).
- Registro de entrenadores con especialidades (HU-05, RF-07).

## [0.1.0] — Sprint 1
### Agregado
- Estructura MVC en Flask, configuración por entorno y modelo de dominio.
- Repositorios de acceso a datos y plantilla base responsiva.
