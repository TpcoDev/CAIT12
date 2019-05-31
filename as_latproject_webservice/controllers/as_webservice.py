# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import http
from odoo import http
from odoo.http import request
# from tabulate import tabulate
import json
import sys
import yaml
import logging
_logger = logging.getLogger(__name__)

from werkzeug import urls
from werkzeug.wsgi import wrap_file


class webservice(http.Controller):
    # @http.route('/webservice/stock1', auth='public', methods=['POST'], type="json", csrf=False)
    @http.route('/webservice/stock1', auth='public', type="http")
    def stock1(self, **post):
        stock_move_model = request.env['stock.move']
        # stock_move_ids = stock_move_model.sudo().search([], limit=10)
        stock_move_ids = stock_move_model.sudo().search([])


        json_dict = {"stock_move":[]}
        for stock_move in stock_move_ids:

            sm = { stock_move.id:[{                    
                    "lote":"indefinido", #Lote/N° de serie
                    "categ_id":stock_move.product_id.product_tmpl_id.categ_id.id, #cod categoria
                    "categoria":stock_move.product_id.product_tmpl_id.categ_id.name, #categoria
                    "rut":"indefinido",#rut (sin digito verificador)
                    "usuario":stock_move.picking_id.partner_id.name, #Nombre usuario
                    "codigo_marca":"indefinido",#cod Marca
                    "marca":"indefinido", #Marca
                    "modelo":"indefinido", #Modelo
                    "referencia_proveedor":"indefinido",#referencia (proveedor)
                    "procesador_at":"indefinido", #Procesador_at
                    "velocidad_at":"indefinido", #Velocidad_at
                    "memoria_at":"indefinido", #Memoria_at
                    "hdd_at":"indefinido", #Hdd_at
                    "costo_compra_at":"indefinido",#Costo compra AT
                    "proveedor":"indefinido",#proveedor
                    "N_factura":"indefinido",#N_factura
                    "fecha_compra_at":"indefinido",#fecha compra AT
                    "fecha_asignacion": stock_move.picking_id.date_done #Fecha asignacion
                    }
                    ]
                }
            json_dict["stock_move"].append(sm)
        return json.dumps(json_dict)

    @http.route('/webservice/stock2', auth='public', type="http")
    def stock2(self, **post):
        current_user = request.env['res.users'].sudo().search([('token', '=', post.get('token'))])

        if not current_user:
            return json.dumps({'error': _('Token Invalido')})
        else:
            stock_picking_model = request.env['stock.picking']
            # stock_picking_ids = stock_picking_model.sudo().search([], limit=10)
            stock_picking_ids = stock_picking_model.sudo().search([])

        json_dict = {"stock_move":[]}
        for stock_move in stock_move_ids:

            sm = { stock_move.id:[{                    
                    "lote":"indefinido", #Lote/N° de serie
                    "categ_id":stock_move.product_id.product_tmpl_id.categ_id.id, #cod categoria
                    "categoria":stock_move.product_id.product_tmpl_id.categ_id.name, #categoria
                    "rut":"indefinido",#rut (sin digito verificador)
                    "usuario":stock_move.picking_id.partner_id.name, #Nombre usuario
                    "codigo_marca":"indefinido",#cod Marca
                    "marca":"indefinido", #Marca
                    "modelo":"indefinido", #Modelo
                    "referencia_proveedor":"indefinido",#referencia (proveedor)
                    "procesador_at":"indefinido", #Procesador_at
                    "velocidad_at":"indefinido", #Velocidad_at
                    "memoria_at":"indefinido", #Memoria_at
                    "hdd_at":"indefinido", #Hdd_at
                    "costo_compra_at":"indefinido",#Costo compra AT
                    "proveedor":"indefinido",#proveedor
                    "N_factura":"indefinido",#N_factura
                    "fecha_compra_at":"indefinido",#fecha compra AT
                    "fecha_asignacion": stock_move.picking_id.date_done #Fecha asignacion
                    }
                    ]
                }
            json_dict["stock_move"].append(sm)    

    @http.route(['/webservice/token',], auth="public", type="http")
    def token(self, **post):
        """
            Para autenticar se deben enviar usuario y password
            servidor.com:8069/webservice/token?login=admin&password=admin
        """
        res = {}
        uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
        if uid:
            user = request.env['res.users'].sudo().browse(uid)
            token = user.get_user_access_token()
            user.token = token
            res['token'] = token
            request.session.logout()
        else:
            res['error'] = "Login o Password erroneo"
        return json.dumps(res)        