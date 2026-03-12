# -*- coding: utf-8 -*-
import logging
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Ventanas de recordatorio: (días_referencia, día_min_ventana, día_max_ventana)
# Evita perder alertas si el cron no corre exactamente en la fecha objetivo.
REMINDER_WINDOWS = [
    (60, 31, 60),
    (30, 16, 30),
    (15,  8, 15),
    (7,   4,  7),
    (3,   2,  3),
    (1,   0,  1),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    maintenance_contract_ids = fields.One2many(
        'partner.maintenance.contract',
        'partner_id',
        string='Contratos de mantenimiento',
    )

    # ── Acción: abrir wizard de importación desde venta ───────────────────────

    def action_open_maintenance_import(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Importar contratos desde orden de venta',
            'res_model': 'partner.maintenance.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id},
        }

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

        for days_ahead, window_min, window_max in REMINDER_WINDOWS:
            date_from = today + relativedelta(days=window_min)
            date_to   = today + relativedelta(days=window_max)

            contracts = self.env['partner.maintenance.contract'].search([
                ('next_maintenance_date', '>=', date_from),
                ('next_maintenance_date', '<=', date_to),
                ('maintenance_active', '=', True),
            ])

            for contract in contracts:
                partner = contract.partner_id
                maintenance_date = contract.next_maintenance_date
                day_label = '1 día' if days_ahead == 1 else '%d días' % days_ahead
                summary = 'Mantenimiento preventivo en ~%s — %s (%s)' % (
                    day_label, partner.name, contract.name,
                )

                # Evitar duplicados: ya existe actividad abierta para esta fecha y contrato
                existing = self.env['mail.activity'].search([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', partner.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('date_deadline', '=', maintenance_date),
                    ('summary', '=', summary),
                ], limit=1)
                if existing:
                    continue

                responsible = (
                    contract.maintenance_responsible_id
                    or self.env.ref('base.user_admin')
                )

                partner.activity_schedule(
                    'partner_maintenance_reminder.activity_type_maintenance',
                    date_deadline=maintenance_date,
                    summary=summary,
                    note=(
                        'El cliente <strong>%s</strong> tiene mantenimiento programado '
                        'para <strong>%s</strong> el <strong>%s</strong>.' % (
                            partner.name,
                            contract.name,
                            maintenance_date.strftime('%d/%m/%Y'),
                        )
                    ),
                    user_id=responsible.id,
                )
                partner.message_post(
                    body=(
                        'Recordatorio automático: mantenimiento de '
                        '<strong>%s</strong> en <strong>%s</strong> (%s).' % (
                            contract.name,
                            day_label,
                            maintenance_date.strftime('%d/%m/%Y'),
                        )
                    ),
                    subtype_xmlid='mail.mt_note',
                )
                _logger.info(
                    'Recordatorio de mantenimiento creado para %s / %s (en ~%d días, fecha: %s)',
                    partner.name, contract.name, days_ahead, maintenance_date,
                )
