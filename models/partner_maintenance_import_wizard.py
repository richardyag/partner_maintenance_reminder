# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class PartnerMaintenanceImportWizard(models.TransientModel):
    _name = 'partner.maintenance.import.wizard'
    _description = 'Importar contratos de mantenimiento desde orden de venta'

    partner_id = fields.Many2one('res.partner', required=True, string='Cliente')
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Orden de venta',
        domain="[('partner_id', '=', partner_id), ('state', 'in', ['sale', 'done'])]",
    )
    contract_date = fields.Date(
        string='Fecha de inicio del contrato',
        default=fields.Date.today,
        required=True,
    )
    line_ids = fields.One2many(
        'partner.maintenance.import.wizard.line',
        'wizard_id',
        string='Productos',
    )
    lines_loaded = fields.Boolean(default=False)

    def action_load_products(self):
        """Carga los productos y números de serie desde la orden de venta seleccionada."""
        if not self.sale_order_id:
            raise UserError('Debe seleccionar una orden de venta.')

        # Limpiar líneas anteriores
        self.line_ids.unlink()

        # Recopilar lotes entregados por producto desde entregas confirmadas
        delivered_lots = {}
        for picking in self.sale_order_id.picking_ids:
            if picking.picking_type_code != 'outgoing' or picking.state != 'done':
                continue
            for ml in picking.move_line_ids:
                if not ml.product_id:
                    continue
                delivered_lots.setdefault(ml.product_id.id, [])
                if ml.lot_id:
                    delivered_lots[ml.product_id.id].append(ml.lot_id)

        seen_lot_ids = set()
        for order_line in self.sale_order_id.order_line:
            product = order_line.product_id
            if not product or product.type == 'service':
                continue
            lots = delivered_lots.get(product.id, [])
            if lots:
                for lot in lots:
                    if lot.id not in seen_lot_ids:
                        seen_lot_ids.add(lot.id)
                        self.env['partner.maintenance.import.wizard.line'].create({
                            'wizard_id': self.id,
                            'product_id': product.id,
                            'lot_id': lot.id,
                            'serial_number': lot.name,
                            'include': False,
                        })
            else:
                self.env['partner.maintenance.import.wizard.line'].create({
                    'wizard_id': self.id,
                    'product_id': product.id,
                    'include': False,
                })

        self.lines_loaded = True

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'partner.maintenance.import.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_create_contracts(self):
        today = fields.Date.today()
        lines_to_create = self.line_ids.filtered('include')
        if not lines_to_create:
            raise UserError('No hay productos seleccionados para crear contratos.')
        missing_interval = lines_to_create.filtered(lambda l: not l.maintenance_interval)
        if missing_interval:
            products = ', '.join(l.product_id.display_name or '?' for l in missing_interval)
            raise UserError('Debe indicar la frecuencia para: %s' % products)
        for line in lines_to_create:
            self.env['partner.maintenance.contract'].create({
                'partner_id': self.partner_id.id,
                'product_id': line.product_id.id,
                'lot_id': line.lot_id.id if line.lot_id else False,
                'serial_number': line.serial_number or '',
                'contract_date': self.contract_date or today,
                'maintenance_interval': line.maintenance_interval,
                'maintenance_responsible_id': line.maintenance_responsible_id.id if line.maintenance_responsible_id else False,
                'maintenance_active': True,
            })
        return {'type': 'ir.actions.act_window_close'}


class PartnerMaintenanceImportWizardLine(models.TransientModel):
    _name = 'partner.maintenance.import.wizard.line'
    _description = 'Línea del asistente de importación de mantenimiento'

    wizard_id = fields.Many2one(
        'partner.maintenance.import.wizard',
        required=True,
        ondelete='cascade',
    )
    include = fields.Boolean(string='Incluir', default=False)
    product_id = fields.Many2one('product.product', string='Producto')
    lot_id = fields.Many2one('stock.lot', string='Lote/Serie (Odoo)')
    serial_number = fields.Char(string='N° serie')
    maintenance_interval = fields.Selection([
        ('6', 'Cada 6 meses'),
        ('12', 'Cada año'),
    ], string='Frecuencia')
    maintenance_responsible_id = fields.Many2one('res.users', string='Responsable')
