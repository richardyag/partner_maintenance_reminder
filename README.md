# Recordatorios de Mantenimiento Preventivo

Módulo para Odoo 19 que permite programar y recibir recordatorios automáticos de mantenimiento preventivo para cada cliente.

---

## ¿Qué hace este módulo?

- Agrega una pestaña **Mantenimiento** en cada contacto (cliente)
- Calcula automáticamente la **fecha del próximo mantenimiento** según la frecuencia configurada
- Genera **recordatorios automáticos** 7 días, 3 días y 1 día antes del vencimiento
- Los recordatorios aparecen en el **chatter del contacto** y en el **panel de actividades** del responsable asignado

---

## Configuración por cliente

### 1. Abrir el contacto

Ir a **Contactos** y abrir el cliente al que se le quiere programar mantenimiento.

### 2. Completar la pestaña Mantenimiento

Dentro del formulario del contacto, hacer clic en la pestaña **Mantenimiento** y completar los siguientes campos:

| Campo | Descripción |
|-------|-------------|
| **Fecha de contrato** | Fecha en que se firmó o inició el contrato de mantenimiento |
| **Frecuencia de mantenimiento** | Cada 6 meses o cada 1 año |
| **Responsable de mantenimiento** | Usuario de Odoo que recibirá los recordatorios |
| **Recordatorios activos** | Debe estar activado (✅) para que el sistema envíe alertas |
| **Último mantenimiento** | Fecha en que se realizó el último mantenimiento (se actualiza con el botón) |
| **Próximo mantenimiento** | Se calcula automáticamente — no se edita manualmente |

### 3. Guardar

Hacer clic en **Guardar**. El campo **Próximo mantenimiento** se calculará automáticamente.

> **Ejemplo:** Si la fecha de contrato es 15/01/2025 y la frecuencia es anual, el próximo mantenimiento será el 15/01/2026.

---

## Cómo se calcula la fecha del próximo mantenimiento

```
Próximo mantenimiento = Último mantenimiento + Frecuencia
                        (o Fecha de contrato si no hay último mantenimiento)
```

---

## Dónde aparecen los recordatorios

El sistema genera recordatorios automáticamente **7 días, 3 días y 1 día antes** de la fecha de vencimiento.

Los recordatorios aparecen en **dos lugares**:

### En el chatter del contacto
Dentro del contacto, en la sección de mensajes (parte inferior), aparece una nota automática indicando que el mantenimiento está próximo a vencer.

### En el panel de actividades del responsable
El ícono de reloj (⏰) en la barra superior de Odoo mostrará un contador con las actividades pendientes. Al hacer clic, el responsable verá el recordatorio con el nombre del cliente y la fecha de vencimiento.

---

## Registrar un mantenimiento realizado

Cuando se completa un mantenimiento:

1. Abrir el contacto
2. Ir a la pestaña **Mantenimiento**
3. Hacer clic en el botón **"Registrar mantenimiento realizado hoy"**

Esto actualiza automáticamente el campo **Último mantenimiento** con la fecha de hoy y recalcula la próxima fecha.

---

## Preguntas frecuentes

**¿Por qué no veo recordatorios de un cliente que cargué?**
Los recordatorios se generan cuando el próximo mantenimiento está a 7, 3 o 1 día de distancia. Si la fecha ya pasó o está a más de 7 días, el sistema esperará hasta que entre en ese rango.

**¿Con qué frecuencia corre el sistema?**
Una vez por día, de forma automática.

**¿Puedo desactivar los recordatorios para un cliente?**
Sí, desactivando el campo **Recordatorios activos** en la pestaña Mantenimiento del contacto.

**¿Qué pasa si no hay responsable asignado?**
El recordatorio se asigna al administrador del sistema.
