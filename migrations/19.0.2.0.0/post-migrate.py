# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migra los datos de contratos existentes en res.partner
    al nuevo modelo partner.maintenance.contract (One2many).
    """
    cr.execute("""
        INSERT INTO partner_maintenance_contract
            (partner_id, name, contract_date, maintenance_interval,
             maintenance_responsible_id, maintenance_active,
             last_maintenance_date, create_uid, write_uid, create_date, write_date)
        SELECT
            id,
            'Contrato principal',
            contract_date,
            maintenance_interval,
            maintenance_responsible_id,
            COALESCE(maintenance_active, true),
            last_maintenance_date,
            1, 1, NOW(), NOW()
        FROM res_partner
        WHERE contract_date IS NOT NULL
          AND maintenance_interval IS NOT NULL
    """)
    cr.execute("SELECT COUNT(*) FROM partner_maintenance_contract")
    count = cr.fetchone()[0]
    _logger.info('Migración: %d contratos creados desde res.partner', count)
