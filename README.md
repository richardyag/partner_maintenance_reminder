# Partner Maintenance Reminder

Módulo para **Odoo 19** que gestiona recordatorios automáticos de mantenimiento preventivo para contactos/clientes.

---

## Funcionalidades

- Pestaña **Mantenimiento** en cada contacto con fecha de contrato, frecuencia e historial
- Cálculo automático de la **fecha del próximo mantenimiento**
- Recordatorios automáticos en **6 momentos**: 60, 30, 15, 7, 3 y 1 día antes del vencimiento
- Actividades asignadas al responsable, visibles en el panel de actividades (⏰)
- Mensaje automático en el chatter del contacto en cada recordatorio
- Al **completar la actividad** desde el reloj: registra el mantenimiento y recalcula la próxima fecha automáticamente

---

## Instalación

1. Copiar el módulo en la carpeta de addons de Odoo
2. Actualizar la lista de módulos
3. Instalar **Partner Maintenance Reminder**

**Dependencias:** `base`, `mail`

---

## Uso rápido

1. Ir a **Contactos** → abrir un cliente
2. Pestaña **Mantenimiento** → completar los campos
3. Guardar → el sistema calcula la próxima fecha automáticamente
4. El cron diario envía actividades al responsable según el calendario de recordatorios

Ver [MANUAL_CLIENTE.md](MANUAL_CLIENTE.md) para la guía completa de uso.

---

## Estructura

```
partner_maintenance_reminder/
├── models/
│   ├── res_partner.py        # Campos y lógica de mantenimiento + cron
│   └── mail_activity.py      # Override action_feedback para registrar mantenimiento al completar
├── data/
│   ├── activity_type.xml     # Tipo de actividad "Mantenimiento Preventivo"
│   └── cron.xml              # Cron diario
└── views/
    └── res_partner_views.xml # Pestaña Mantenimiento en el formulario de contactos
```

---

## Licencia

LGPL-3 — Econovex
