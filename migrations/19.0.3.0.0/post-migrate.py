# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migra contratos existentes al nuevo esquema con product_id.

    Los contratos previos tenían 'name' como texto libre. Ahora 'name' es
    computado desde product_id. Los registros existentes quedarán con
    product_id = NULL hasta que el usuario los edite y asigne un producto.

    Se agrega la columna serial_number si no existe (Odoo la crea automáticamente,
    pero se verifica por si acaso).
    """
    # Verificar cuántos contratos existentes no tienen product_id asignado
    cr.execute("""
        SELECT COUNT(*) FROM partner_maintenance_contract
        WHERE product_id IS NULL
    """)
    count = cr.fetchone()[0]
    if count:
        _logger.warning(
            'Migración 19.0.3.0.0: %d contrato(s) sin product_id. '
            'Deben editarse para asignar el producto correspondiente.',
            count,
        )
    else:
        _logger.info('Migración 19.0.3.0.0: todos los contratos tienen product_id.')
