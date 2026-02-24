# Manual de uso — Recordatorios de Mantenimiento Preventivo

---

## ¿Para qué sirve este módulo?

Permite registrar en cada cliente la fecha y frecuencia de su contrato de mantenimiento. El sistema avisa automáticamente al responsable cuando se acerca el vencimiento, con tiempo suficiente para planificar la visita.

---

## Paso 1 — Configurar el mantenimiento de un cliente

### 1.1 Abrir el contacto

Ir al menú **Contactos** y buscar el cliente al que se le quiere configurar el mantenimiento.

### 1.2 Completar la pestaña Mantenimiento

Dentro del formulario del contacto, hacer clic en la pestaña **Mantenimiento**.

Completar los siguientes campos:

| Campo | Qué ingresar |
|-------|-------------|
| **Fecha de contrato** | Fecha en que inició el contrato de mantenimiento con este cliente |
| **Frecuencia de mantenimiento** | Seleccionar **Cada 6 meses** o **Cada año** |
| **Responsable de mantenimiento** | Usuario de Odoo que recibirá los recordatorios |
| **Recordatorios activos** | Dejar activado ✅ para que el sistema envíe alertas |
| **Último mantenimiento** | Si ya se realizó algún mantenimiento, ingresar la fecha del último |

El campo **Próximo mantenimiento** se calcula automáticamente — no se edita.

### 1.3 Guardar

Hacer clic en **Guardar** (o el botón de guardado de la barra superior).

El campo **Próximo mantenimiento** se actualizará automáticamente con la fecha calculada.

> **Ejemplo:**
> - Fecha de contrato: 01/03/2025
> - Frecuencia: Cada año
> - Último mantenimiento: (vacío)
> - **Próximo mantenimiento: 01/03/2026**

> **Ejemplo con mantenimiento previo:**
> - Frecuencia: Cada 6 meses
> - Último mantenimiento: 10/08/2025
> - **Próximo mantenimiento: 10/02/2026**

---

## Paso 2 — Cómo funcionan los recordatorios

El sistema verifica todos los días los vencimientos próximos y genera alertas automáticas en los siguientes momentos:

| Cuándo llega el aviso | Días restantes |
|---|---|
| 2 meses antes | 60 días |
| 1 mes antes | 30 días |
| 2 semanas antes | 15 días |
| 1 semana antes | 7 días |
| 3 días antes | 3 días |
| 1 día antes | 1 día |

Cada aviso crea una actividad asignada al **Responsable de mantenimiento** configurado en el contacto.

---

## Paso 3 — Dónde ver los recordatorios

### En el ícono de reloj (⏰)

En la barra superior de Odoo, el ícono de reloj muestra un número rojo con la cantidad de actividades pendientes asignadas al usuario.

Al hacer clic aparece la lista de actividades. Cada recordatorio de mantenimiento muestra:
- El nombre del cliente
- La fecha de vencimiento del mantenimiento
- Cuántos días faltan (ej: "en 7 días")

### En el chatter del contacto

Dentro del contacto, en la sección de mensajes (parte inferior), aparecen notas automáticas cada vez que el sistema genera un recordatorio. Allí queda el historial completo.

---

## Paso 4 — Marcar el mantenimiento como realizado

Hay **dos formas** de registrar que el mantenimiento fue completado:

### Opción A — Desde el reloj ⏰ (recomendada)

1. Hacer clic en el ícono ⏰ en la barra superior
2. Buscar la actividad del cliente correspondiente
3. Hacer clic en el ícono ✓ (marcar como hecha)
4. Completar el campo de comentario si se desea y confirmar

**El sistema automáticamente:**
- Registra la fecha de hoy como **Último mantenimiento**
- Recalcula la **Próxima fecha** (hoy + 6 o 12 meses)
- Cancela los demás avisos pendientes del mismo cliente
- Agrega una nota en el chatter con la nueva fecha calculada

### Opción B — Desde el contacto

1. Abrir el contacto
2. Ir a la pestaña **Mantenimiento**
3. Hacer clic en el botón **"Registrar mantenimiento realizado hoy"**

---

## Preguntas frecuentes

**¿Por qué no veo ningún aviso de un cliente que acabo de cargar?**

Los recordatorios se generan cuando el próximo mantenimiento cae dentro de las ventanas de 60, 30, 15, 7, 3 o 1 día. Si la fecha está a más de 60 días o ya pasó, el sistema esperará hasta que entre en alguna de esas ventanas.

**¿Qué pasa si el mantenimiento ya venció?**

El sistema no genera avisos retroactivos. Para regularizar un cliente con fecha vencida, usar el botón **"Registrar mantenimiento realizado hoy"** en la pestaña Mantenimiento, o actualizar manualmente el campo **Último mantenimiento** con la fecha real en que se realizó.

**¿Puedo pausar los avisos de un cliente sin perder la configuración?**

Sí. En la pestaña Mantenimiento, desactivar el campo **Recordatorios activos**. El sistema dejará de enviar alertas para ese cliente pero mantendrá todos los datos. Para reactivar, volver a activar el campo.

**¿Qué pasa si no hay responsable asignado?**

El recordatorio se asigna al administrador del sistema.

**¿Con qué frecuencia corre el sistema?**

Una vez por día, de forma automática. Si se necesita verificar manualmente, un administrador puede ejecutar el proceso desde Ajustes → Técnico → Automatización → Acciones Programadas → *Recordatorios de Mantenimiento Preventivo* → Ejecutar manualmente.

---

*Econovex — soporte: https://www.econovex.com*
