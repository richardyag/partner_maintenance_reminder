{
    'name': 'Partner Maintenance Reminder',
    'version': '19.0.4.0.0',
    'category': 'Sales/CRM',
    'summary': 'Recordatorios periódicos de mantenimiento preventivo para clientes',
    'description': """
        Gestión de recordatorios de mantenimiento preventivo para contactos.

        Funcionalidades:
        - Fecha de contrato y frecuencia de mantenimiento (6 o 12 meses) por cliente
        - Recordatorios automáticos 7, 3 y 1 día antes del vencimiento
        - Actividades asignadas al responsable, visibles en su panel de trabajo
        - Historial completo en el chatter del contacto
    """,
    'author': 'Econovex',
    'website': 'https://www.econovex.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'stock', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/activity_type.xml',
        'data/cron.xml',
        'views/partner_maintenance_import_wizard_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
