# -*- coding: utf-8 -*-
import logging
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PartnerMaintenanceContract(models.Model):
    _name = 'partner.maintenance.contract'
    _description = 'Contrato de mantenimiento'
    _order = 'contract_date'

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Equipo / Producto',
        required=True,
    )
    name = fields.Char(
        string='Equipo / Descripción',
        compute='_compute_name',
        store=True,
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='N° de serie',
        domain="[('product_id', '=', product_id)]",
    )
    serial_number = fields.Char(
        string='N° serie (manual)',
    )
    contract_date = fields.Date(
        string='Fecha de inicio',
        required=True,
    )
    maintenance_interval = fields.Selection([
        ('6', 'Cada 6 meses'),
        ('12', 'Cada año'),
    ], string='Frecuencia', required=True)

    maintenance_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
    )
    maintenance_active = fields.Boolean(
        string='Activo',
        default=True,
    )
    last_maintenance_date = fields.Date(
        string='Último mantenimiento',
    )
    next_maintenance_date = fields.Date(
        string='Próximo mantenimiento',
        compute='_compute_next_maintenance_date',
        store=True,
    )

    # ── Cómputo ──────────────────────────────────────────────────────────────

    @api.depends('product_id')
    def _compute_name(self):
        for contract in self:
            contract.name = contract.product_id.display_name or ''

    @api.depends('contract_date', 'maintenance_interval', 'last_maintenance_date')
    def _compute_next_maintenance_date(self):
        for contract in self:
            if not contract.contract_date or not contract.maintenance_interval:
                contract.next_maintenance_date = False
                continue
            base_date = contract.last_maintenance_date or contract.contract_date
            months = int(contract.maintenance_interval)
            contract.next_maintenance_date = base_date + relativedelta(months=months)

    # ── Onchange ─────────────────────────────────────────────────────────────

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            self.serial_number = self.lot_id.name

    # ── Acción manual: registrar mantenimiento realizado ─────────────────────

    def action_register_maintenance(self):
        """Marca el mantenimiento como realizado hoy y recalcula la próxima fecha."""
        today = fields.Date.today()
        for contract in self:
            contract.last_maintenance_date = today
            contract.partner_id.message_post(
                body=(
                    'Mantenimiento registrado para <strong>%s</strong> '
                    'el <strong>%s</strong>.' % (
                        contract.name,
                        today.strftime('%d/%m/%Y'),
                    )
                ),
                subtype_xmlid='mail.mt_note',
            )
        return True
