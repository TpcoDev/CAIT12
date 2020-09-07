# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta

class as_HelpdeskTicket(models.Model):
    _inherit = 'stock.production.lot'

    as_quant_ids = fields.One2many('stock.quant', 'lot_id', string='Movimientos de Lote',domain=[('quantity', '>', 0),('location_id.usage', '=','internal')])

class as_HelpdeskTicket(models.Model):
    _inherit = 'stock.quant'

    as_studio_direccin_jerrquica = fields.Char(string='Dirección Jerárquica')
    as_studio_n_factura = fields.Char(string='N Factura')