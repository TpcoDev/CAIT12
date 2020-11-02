# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare    
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('product_id')
    @api.depends('product_id')
    def _valida_lote_product(self):
        for move in self:
            conta = 0
            for move_line in move.picking_id.move_line_ids_without_package:
                if move.product_id.id ==move_line.product_id.id and move.lot_id.id ==move_line.lot_id.id:
                    conta+=1
            if conta > 1:
                raise UserError(_("No esta permitido dos registros, mismo producto, mismo lote."))

    @api.multi
    @api.onchange('lot_id')
    @api.depends('lot_id')
    def _quant_lotes(self):
        for route in self:
            ubicaciones=[]
            location_id = route.picking_id.location_id.id
            product_id = route.product_id
            self.env.cr.execute("SELECT lot_id FROM stock_quant where quantity >0 and  location_id="+str(location_id))
            product_ids=self.env.cr.fetchall()
            if product_ids:
                for product in product_ids:
                    ubicaciones.append(product[0])       
                route.product_id = route.lot_id.product_id
                return {'domain':{'lot_id': [('id','in', tuple(ubicaciones))]}}
            else:
                return []

    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', store=True,)

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    @api.onchange('product_id','product_uom_qty')
    @api.depends('product_id','product_uom_qty')
    def _get_product_id(self):
        for quant in self:
            ubicaciones=[]
            location_id = quant.location_id.id
            product_id = quant.product_id
            self.env.cr.execute("SELECT product_id FROM stock_quant where quantity >0 and location_id="+str(location_id))
            product_ids=self.env.cr.fetchall()
            _logger.debug('\n\n\n\nentro a el dmain')
            if product_ids:
                for product in product_ids:
                    ubicaciones.append(product[0])       
                return {'domain':{'product_id': [('id','in', tuple(ubicaciones)),('type', 'in', ['product', 'consu'])]}}
            else:
                return [('type', 'in', ['product', 'consu'])]

    def _default_product_id(self):
        for quant in self:
            ubicaciones=[]
            location_id = quant.picking_id.location_id.id
            product_id = quant.product_id
            self.env.cr.execute("SELECT product_id FROM stock_quant where quantity >0 and location_id="+str(location_id))
            product_ids=self.env.cr.fetchall()
            if product_ids:
                for product in product_ids:
                    ubicaciones.append(product[0])       
                quant.product_id = self.env['product.product'].search([('id','in', tuple(ubicaciones))])
            else:
                quant.product_id = self.env['product.product']
    
    product_id = fields.Many2one('product.product', 'Producto', store=True, index=True, required=True,
        states={'done': [('readonly', True)]})

