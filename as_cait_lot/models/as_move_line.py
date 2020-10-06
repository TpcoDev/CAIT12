# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare    
from datetime import datetime, timedelta, date

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('lot_id')
    def _rutas_dominio(self):
        for route in self:
            ubicaciones=[]
            location_id = route.picking_id.location_id.id
            product_id = route.product_id
            self.env.cr.execute("SELECT lot_id FROM stock_quant where location_id="+str(location_id))
            product_ids=self.env.cr.fetchall()
            if product_ids:
                for product in product_ids:
                    ubicaciones.append(product[0])       
                if ubicaciones:
                    if len(ubicaciones)>0:
                        self.update({
                            'lot_id': ubicaciones[0],
                        })
                #return  [('id', 'in', tuple(rutas_permitidas))]
                product_id = self.env['stock.production.lot'].search([('id', '=', ubicaciones[0])])
                route.product_id = product_id.product_id
                return {'domain':{'lot_id': [('id','in', tuple(ubicaciones))]}}
            else:
                return []

    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', domain=_rutas_dominio)