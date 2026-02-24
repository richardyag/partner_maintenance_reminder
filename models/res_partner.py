# -*- coding: utf-8 -*-
import logging
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

REMINDER_DAYS = (60, 30, 15, 7, 3, 1)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ── Campos de mantenimiento ───────────────────────────────────────────────

    contract_date = fields.Date(
        string='Fecha de contrato',
        tracking=True,
    )
    maintenance_interval = fields.Selection([
        ('6', 'Cada 6 meses'),
        ('12', 'Cada año'),
    ], string='Frecuencia de mantenimiento', tracking=True)

    maintenance_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable de mantenimiento',
        tracking=True,
    )
    maintenance_active = fields.Boolean(
        string='Recordatorios activos',
        default=True,
    )

    last_maintenance_date = fields.Date(
        string='Último mantenimiento',
        tracking=True,
    )
    next_maintenance_date = fields.Date(
        string='Próximo mantenimiento',
        compute='_compute_next_maintenance_date',
        store=True,
    )

    # ── Cómputo ──────────────────────────────────────────────────────────────

    @api.depends('contract_date', 'maintenance_interval', 'last_maintenance_date')
    def _compute_next_maintenance_date(self):
        for partner in self:
            if not partner.contract_date or not partner.maintenance_interval:
                partner.next_maintenance_date = False
                continue
            base_date = partner.last_maintenance_date or partner.contract_date
            months = int(partner.maintenance_interval)
            partner.next_maintenance_date = base_date + relativedelta(months=months)

    # ── Acción manual: registrar mantenimiento realizado ─────────────────────

    def action_register_maintenance(self):
        """Marca el mantenimiento como realizado hoy y recalcula la próxima fecha."""
        today = fields.Date.today()
        for partner in self:
            partner.last_maintenance_date = today
            partner.message_post(
                body='Mantenimiento registrado manualmente el <strong>%s</strong>.' % today.strftime('%d/%m/%Y'),
                subtype_xmlid='mail.mt_note',
            )
        return True

    # ── Cron diario ──────────────────────────────────────────────────────────

    @api.model
    def _cron_send_maintenance_reminders(self):
        today = fields.Date.today()
        activity_type = self.env.ref(
            'partner_maintenance_reminder.activity_type_maintenance',
            raise_if_not_found=False,
        )
        if not activity_type:
            _logger.warning('Tipo de actividad de mantenimiento no encontrado')
            return

        # Límites de cada ventana (no superpuestos, del más lejano al más cercano)
        # 30d: ]7, 30]  7d: ]3, 7]  3d: ]1, 3]  1d: [0, 1]
        windows = [
            (60, 31, 60),
            (30, 16, 30),
            (15,  8, 15),
            (7,   4,  7),
            (3,   2,  3),
            (1,   0,  1),
        ]

        for days_ahead, window_min, window_max in windows:
            date_from = today + relativedelta(days=window_min)
            date_to   = today + relativedelta(days=window_max)

            partners = self.search([
                ('next_maintenance_date', '>=', date_from),
                ('next_maintenance_date', '<=', date_to),
                ('maintenance_active', '=', True),
                ('contract_date', '!=', False),
                ('maintenance_interval', '!=', False),
            ])
            for partner in partners:
                maintenance_date = partner.next_maintenance_date
                # Evitar duplicados: ya existe actividad abierta para esta fecha
                existing = self.env['mail.activity'].search([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', partner.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('date_deadline', '=', maintenance_date),
                ], limit=1)
                if existing:
                    continue

                responsible = (
                    partner.maintenance_responsible_id or self.env.ref('base.user_admin')
                )
                day_label = '1 día' if days_ahead == 1 else '%d días' % days_ahead

                partner.activity_schedule(
                    'partner_maintenance_reminder.activity_type_maintenance',
                    date_deadline=maintenance_date,
                    summary='Mantenimiento preventivo en %s — %s' % (day_label, partner.name),
                    note=(
                        'El cliente <strong>%s</strong> tiene mantenimiento programado '
                        'para el <strong>%s</strong>.' % (
                            partner.name,
                            maintenance_date.strftime('%d/%m/%Y'),
                        )
                    ),
                    user_id=responsible.id,
                )
                partner.message_post(
                    body=(
                        'Recordatorio automático: mantenimiento en '
                        '<strong>%s</strong> (%s).' % (
                            day_label,
                            maintenance_date.strftime('%d/%m/%Y'),
                        )
                    ),
                    subtype_xmlid='mail.mt_note',
                )
                _logger.info(
                    'Recordatorio de mantenimiento creado para %s (en ~%d días, fecha: %s)',
                    partner.name, days_ahead, maintenance_date,
                )
