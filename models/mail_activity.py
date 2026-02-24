# -*- coding: utf-8 -*-
from odoo import fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_feedback(self, feedback=False, attachment_ids=None):
        """Al completar una actividad de mantenimiento, registra la fecha
        en el contacto y recalcula el próximo vencimiento."""
        maintenance_type = self.env.ref(
            'partner_maintenance_reminder.activity_type_maintenance',
            raise_if_not_found=False,
        )

        # Recopilar IDs ANTES de que super() elimine las actividades
        partner_ids = []
        if maintenance_type:
            partner_ids = [
                act.res_id for act in self
                if act.activity_type_id == maintenance_type
                and act.res_model == 'res.partner'
            ]

        result = super().action_feedback(
            feedback=feedback, attachment_ids=attachment_ids
        )

        if partner_ids:
            today = fields.Date.today()
            partners = self.env['res.partner'].sudo().browse(partner_ids).exists()
            for partner in partners:
                # Actualizar fecha → dispara recompute de next_maintenance_date
                partner.last_maintenance_date = today

                # Cancelar otras actividades de mantenimiento pendientes
                # (ej: si se marcó el de 30 días, eliminar los de 7/3/1)
                pending = self.env['mail.activity'].sudo().search([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', partner.id),
                    ('activity_type_id', '=', maintenance_type.id),
                ])
                if pending:
                    pending.unlink()

                # Mensaje en el chatter con la nueva fecha calculada
                partner._compute_next_maintenance_date()
                next_date = partner.next_maintenance_date
                partner.message_post(
                    body=(
                        'Mantenimiento completado el <strong>%s</strong>. '
                        'Próximo mantenimiento programado para: <strong>%s</strong>.'
                        % (
                            today.strftime('%d/%m/%Y'),
                            next_date.strftime('%d/%m/%Y') if next_date else '—',
                        )
                    ),
                    subtype_xmlid='mail.mt_note',
                )

        return result
