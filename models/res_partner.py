# -*- coding: utf-8 -*-
import logging
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

REMINDER_DAYS = (7, 3, 1)


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

        for days_ahead in REMINDER_DAYS:
            target_date = today + relativedelta(days=days_ahead)
            partners = self.search([
                ('next_maintenance_date', '=', target_date),
                ('maintenance_active', '=', True),
                ('contract_date', '!=', False),
                ('maintenance_interval', '!=', False),
            ])
            for partner in partners:
                # Evitar actividades duplicadas para el mismo vencimiento
                existing = self.env['mail.activity'].search([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', partner.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('date_deadline', '=', target_date),
                ], limit=1)
                if existing:
                    continue

                responsible = partner.maintenance_responsible_id or self.env.ref('base.user_admin')
                day_label = '1 día' if days_ahead == 1 else '%d días' % days_ahead

                partner.activity_schedule(
                    'partner_maintenance_reminder.activity_type_maintenance',
                    date_deadline=target_date,
                    summary='Mantenimiento preventivo en %s — %s' % (day_label, partner.name),
                    note=(
                        'El cliente <strong>%s</strong> tiene mantenimiento programado '
                        'para el <strong>%s</strong>.' % (
                            partner.name,
                            target_date.strftime('%d/%m/%Y'),
                        )
                    ),
                    user_id=responsible.id,
                )
                partner.message_post(
                    body=(
                        'Recordatorio automático: mantenimiento en '
                        '<strong>%s</strong> (%s).' % (
                            day_label,
                            target_date.strftime('%d/%m/%Y'),
                        )
                    ),
                    subtype_xmlid='mail.mt_note',
                )
                _logger.info(
                    'Recordatorio de mantenimiento creado para %s (en %d días, fecha: %s)',
                    partner.name, days_ahead, target_date,
                )
