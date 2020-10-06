# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    as_quant_ids = fields.One2many('stock.quant', 'lot_id', string='Movimientos de Lote',domain=[('quantity', '>', 0),('location_id.usage', '=','internal')])

    @api.model
    def create(self, vals):
        rec = super(StockProductionLot, self).create(vals)
        for lote in rec:
            if lote.name:
                self.env.cr.execute('''
                    SELECT
                    lt.name
                    FROM stock_production_lot AS lt
                    WHERE (lt.name = %s ) and lt.id != %s
                    LIMIT 1
                ''',([str(lote.name),str(lote.id)]))
                legal_name = [i for i in self.env.cr.fetchall()]
                if legal_name:
                    raise UserError(_("El Lote: " + str(legal_name[0][0]) + " ya existe en la Base de Datos."))
        return rec

    @api.multi
    def write(self, vals):
        res =super(StockProductionLot, self).write(vals)
        for lote in self:
            if lote.name:
                self.env.cr.execute('''
                    SELECT
                    lt.name
                    FROM stock_production_lot AS lt
                    WHERE (lt.name = %s ) and lt.id != %s
                    LIMIT 1
                ''',([str(lote.name),str(lote.id)]))
                legal_name = [i for i in self.env.cr.fetchall()]
                if legal_name:
                    raise UserError(_("El Lote: " + str(legal_name[0][0]) + " ya existe en la Base de Datos."))
        return res

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    x_studio_direccin_jerrquica = fields.Char(string='Dirección Jerárquica')
    x_studio_n_factura = fields.Integer(string='N Factura')