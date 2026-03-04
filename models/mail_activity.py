# -*- coding: utf-8 -*-
from odoo import fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_feedback(self, feedback=False, attachment_ids=None):
        """Al completar una actividad de mantenimiento, registra la fecha en el
        contrato correspondiente y cancela otras alertas pendientes del mismo."""
        maintenance_type = self.env.ref(
            'partner_maintenance_reminder.activity_type_maintenance',
            raise_if_not_found=False,
        )

        # Recopilar (partner_id, date_deadline) ANTES de que super() elimine las actividades
        to_update = []
        if maintenance_type:
            to_update = [
                (act.res_id, act.date_deadline) for act in self
                if act.activity_type_id == maintenance_type
                and act.res_model == 'res.partner'
            ]

        result = super().action_feedback(
            feedback=feedback, attachment_ids=attachment_ids
        )

        if to_update:
            today = fields.Date.today()
            for partner_id, deadline in to_update:
                partner = self.env['res.partner'].sudo().browse(partner_id).exists()
                if not partner:
                    continue

                # Encontrar el contrato cuyo próximo mantenimiento coincide con la actividad
                contract = self.env['partner.maintenance.contract'].sudo().search([
                    ('partner_id', '=', partner_id),
                    ('next_maintenance_date', '=', deadline),
                ], limit=1)

                if not contract:
                    continue

                # Actualizar fecha → dispara recompute de next_maintenance_date
                contract.last_maintenance_date = today

                # Cancelar otras actividades de mantenimiento pendientes de este contrato
                pending = self.env['mail.activity'].sudo().search([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', partner_id),
                    ('activity_type_id', '=', maintenance_type.id),
                    ('summary', 'like', contract.name),
                ])
                if pending:
                    pending.unlink()

                # Mensaje en el chatter con la nueva fecha calculada
                contract._compute_next_maintenance_date()
                next_date = contract.next_maintenance_date
                partner.message_post(
                    body=(
                        'Mantenimiento de <strong>%s</strong> completado el <strong>%s</strong>. '
                        'Próximo mantenimiento programado para: <strong>%s</strong>.'
                        % (
                            contract.name,
                            today.strftime('%d/%m/%Y'),
                            next_date.strftime('%d/%m/%Y') if next_date else '—',
                        )
                    ),
                    subtype_xmlid='mail.mt_note',
                )

        return result
