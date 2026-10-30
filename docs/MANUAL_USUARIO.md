# Manual de usuario · GymControl

GymControl ayuda al gimnasio a registrar socios, controlar quién entra según su membresía y hacer seguimiento
del progreso físico. Este manual explica cada pantalla según tu rol.

| Si eres… | Lee las secciones |
| --- | --- |
| Recepcionista | 1, 2, 3, 4 |
| Administrador | 1, 2, 5, 6, 7 (y también 3 y 4) |
| Entrenador | 1, 2, 8 |
| Socio | 1, 9 |

## 1. Iniciar sesión

1. Abre GymControl en el navegador (por ejemplo `http://127.0.0.1:5000`).
2. Escribe tu **correo** y tu **contraseña** y presiona **Ingresar**.

![Pantalla de inicio de sesión](capturas/01_login.png)

Si el correo o la contraseña no coinciden, verás el aviso "Usuario o contraseña incorrectos". Por seguridad, el
sistema no indica cuál de los dos datos falló.

![Error de inicio de sesión](capturas/02_login_error.png)

**Primer ingreso de un socio o entrenador.** La contraseña inicial es su número de documento. Se recomienda
cambiarla en **Mi cuenta** (menú lateral): escribe la contraseña actual, la nueva (mínimo 8 caracteres) y su confirmación.

Para salir, usa **Cerrar sesión** en el menú lateral.

## 2. Panel de inicio

Al entrar, el personal ve el resumen del día: socios registrados, membresías activas, membresías que vencen en los
próximos 7 días, socios morosos y los últimos ingresos.

![Panel de inicio de la recepción](capturas/03_inicio_recepcion.png)

El menú lateral muestra solo los módulos de tu rol. En tableta o celular, el menú se abre con el botón ☰.

## 3. Validar el acceso de un socio (recepción)

1. En el menú, elige **Validar acceso**.
2. Digita o escanea el documento del socio.
3. Presiona **Validar acceso** (o la tecla Enter).

El resultado aparece en pocos segundos con un color fácil de ver desde la puerta:

| Color | Significado | Qué hacer |
| --- | --- | --- |
| Verde | Acceso permitido. Muestra el nombre y la fecha de vencimiento | Dejar pasar |
| Ámbar | Acceso permitido, pero la membresía vence en 7 días o menos | Dejar pasar y recordarle renovar |
| Rojo · membresía vencida | Acceso denegado | Remitir a administración para renovar |
| Rojo · socio no registrado | El documento no existe en el sistema | Orientar al visitante hacia el registro |

![Acceso permitido](capturas/04_acceso_permitido.png)

![Acceso permitido con membresía por vencer](capturas/05_acceso_por_vencer.png)

![Acceso denegado por membresía vencida](capturas/06_acceso_denegado.png)

![Documento no registrado](capturas/07_acceso_no_registrado.png)

Cada validación, permitida o denegada, queda guardada en **Últimos ingresos** con la hora y quién la hizo.

La pantalla también funciona en la tableta de recepción:

![Validación de acceso en tableta](capturas/23_tableta_acceso.png)

## 4. Registrar un socio nuevo (recepción)

1. En el menú, elige **Registrar socio**.
2. Completa nombres, apellidos, documento, teléfono y correo. Todos son obligatorios.
3. Presiona **Guardar**.

Si todo está bien, el sistema muestra un mensaje de éxito con el usuario y la contraseña temporal del socio, y lo
agrega al listado.

![Socio registrado con éxito](capturas/09_registro_exitoso.png)

Si falta algún dato o tiene un formato inválido, el campo se marca en rojo con la explicación:

![Campos obligatorios vacíos](capturas/10_registro_campos_vacios.png)

Si el documento ya pertenece a otra persona, el sistema no permite el registro:

![Documento duplicado](capturas/08_registro_duplicado.png)

Después del registro, el administrador debe asignarle una membresía (sección 5) para que pueda ingresar.

## 5. Consultar socios y renovar membresías (administración)

En **Socios** puedes buscar por nombre o documento y ver el estado de cada membresía.

![Listado de socios](capturas/12_listado_socios.png)

Presiona **Ver** para abrir el detalle del socio: membresía actual, historial de membresías con su pago y
últimos ingresos.

![Detalle de un socio](capturas/13_detalle_socio.png)

**Para asignar o renovar una membresía:**

1. En el detalle del socio, presiona **Renovar membresía**.
2. Elige el plan (Mensual, Trimestral o Anual). El monto se completa con el precio del plan; ajústalo si recibiste otro valor.
3. Elige el método de pago: efectivo, transferencia o datáfono.
4. Presiona **Confirmar renovación**.

![Formulario de renovación](capturas/14_renovar_formulario.png)

La nueva membresía empieza hoy y vence según la duración del plan. La anterior queda como "Renovada" en el historial.

![Renovación confirmada](capturas/15_renovar_exito.png)

**Cancelar una membresía.** En el detalle del socio, si la membresía está activa, aparece **Cancelar membresía**.
El sistema pide confirmación y, una vez cancelada, el socio no podrá ingresar.

**Restablecer la contraseña de un socio.** En la misma ficha, **Restablecer contraseña del socio** devuelve su contraseña al número de documento.

## 6. Registrar entrenadores (administración)

1. En el menú, elige **Entrenadores** y luego **Registrar entrenador**.
2. Completa los datos personales y selecciona una o más especialidades.
3. Presiona **Guardar**.

![Registro de entrenador](capturas/16_entrenador_formulario.png)

El entrenador queda activo en el listado y puede iniciar sesión con su correo y su documento como contraseña inicial.

![Listado de entrenadores](capturas/17_entrenadores_listado.png)

## 7. Reporte de socios morosos (administración)

1. En el menú, elige **Reportes**.
2. En **Filtro**, elige "Socios con membresía vencida" (o "Socios con membresía activa").
3. Presiona **Generar reporte**.

El reporte muestra nombre, teléfono, fecha de vencimiento y días de mora. Con **Exportar CSV** lo descargas para
abrirlo en Excel. Si no hay socios vencidos, el sistema lo indica.

![Reporte de morosos](capturas/18_reporte_morosos.png)

## 8. Registrar métricas físicas (entrenador)

1. En **Socios**, busca al socio y presiona **Ver**.
2. Presiona **Control físico**.
3. Escribe el peso en kilogramos y la altura en metros (por ejemplo 1.75). El porcentaje de grasa es opcional.
4. Presiona **Guardar y calcular IMC**.

![Formulario de métricas](capturas/19_metricas_formulario.png)

El sistema calcula el índice de masa corporal (IMC = peso / altura²), lo clasifica según la OMS y lo guarda con la
fecha de hoy. A la derecha ves el historial completo.

![IMC calculado y historial](capturas/20_metricas_imc.png)

| IMC | Clasificación |
| --- | --- |
| Menor que 18,5 | Bajo peso |
| 18,5 a 24,9 | Normal |
| 25 a 29,9 | Sobrepeso |
| 30 o más | Obesidad |

## 9. Consultar mi progreso (socio)

Al iniciar sesión como socio entras directamente a **Mi progreso**. Ahí ves el estado de tu membresía, tu peso e
IMC actuales, una gráfica de la evolución del peso y el historial de mediciones.

![Mi progreso](capturas/21_mi_progreso.png)

Si aún no tienes evaluaciones, verás un mensaje indicándolo:

![Socio sin mediciones](capturas/22_progreso_sin_mediciones.png)

## 10. Preguntas frecuentes

**¿Qué pasa si un socio paga antes de que se venza su membresía?** El administrador la renueva normalmente; la nueva
membresía empieza ese día y la anterior queda como renovada.

**¿Puedo ver quién dejó entrar a un socio?** Sí. En el detalle del socio y en el panel de inicio, cada ingreso muestra
la hora y el nombre de quien lo validó.

**Olvidé mi contraseña.** Si eres socio, pide al administrador que la restablezca desde tu ficha: vuelve a ser tu número de documento. Si eres parte del personal, el administrador del sistema debe restablecerla directamente en la base de datos; la recuperación por correo no hace parte del MVP.

**¿Necesito internet?** No para usar la aplicación en la red del gimnasio; solo el equipo servidor debe estar encendido.
