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
        ids = self.sql_ids_stock_move_line
        stock_move_model = request.env['stock.move.line']
        # stock_move_ids = stock_move_model.sudo().search([], limit=10)
        # stock_move_ids = stock_move_model.sudo().search([('id','in',ids)])
        stock_move_ids = stock_move_model.sudo().search([],limit=500)


        json_dict = {"stock_move_line":[]}
        for stock_move in stock_move_ids:

            sm = { stock_move.id:[{     
                    "lote": stock_move.lot_id.name or "", #Lote/N° de serie
                    "categ_id": stock_move.product_id.product_tmpl_id.categ_id.x_studio_field_B5Yrj or "", #cod categoria
                    "categoria": stock_move.product_id.product_tmpl_id.categ_id.name or "", #categoria
                    # "rut": stock_move.location_dest_id_barcode or "", #rut (sin digito verificador)
                    "usuario": stock_move.picking_id.partner_id.name or "", #Nombre usuario
                    "codigo_marca": stock_move.product_id.product_tmpl_id.x_studio_field_To4X6.x_cod_marcas_de_at or "", #cod Marca
                    "marca": stock_move.product_id.product_tmpl_id.x_studio_field_To4X6.x_name or "",#Marca
                    # "modelo": stock_move.product_id.product_tmpl_id.x_studio_field_5Bj0L.x_studio_field_5BjOL.x_name or "", #Modelo
                    "referencia_proveedor": stock_move.lot_id.ref or "", #referencia (proveedor)
                    "procesador_at": stock_move.product_id.product_tmpl_id.x_studio_field_E6Mvt.x_name or "", #Procesador_at
                    "velocidad_at": stock_move.product_id.product_tmpl_id.x_studio_field_q1N0G.x_name or "", #Velocidad_at
                    # "memoria_at": stock_move.product_id.product_tmpl_id.x_studio_field_INFQG.x_name or "", #Memoria_at
                    "hdd_at": stock_move.product_id.product_tmpl_id.x_studio_field_WRME0.x_name or "", #Hdd_at
                    "costo_compra_at": stock_move.lot_id.x_studio_costo_compra or "", #Costo compra AT
                    # "proveedor": stock_move.lot_id.purchase_order_ids[0].partner_id.name or "",#proveedor
                    "N_factura": stock_move.lot_id.x_studio_n_factura or "",#N_factura
                    "fecha_compra_at": str(stock_move.lot_id.x_studio_field_6Pp3S),#fecha compra AT
                    "fecha_asignacion": str(stock_move.date) #Fecha asignacion
                    }
                    ]
                }
            json_dict["stock_move_line"].append(sm)
        return json.dumps(json_dict)

    @http.route('/webservice/stock2', auth='public', type="http")
    def stock2(self, **post):
        current_user = request.env['res.users'].sudo().search([('token', '=', post.get('token'))])

        if not current_user:
            return json.dumps({'error': _('Token Invalido')})
        else:
            ids = self.sql_ids_stock_move_line
            stock_move_model = request.env['stock.move.line']
            # stock_move_ids = stock_move_model.sudo().search([], limit=10)
            # stock_move_ids = stock_move_model.sudo().search([('id','in',ids)])
            stock_move_ids = stock_move_model.sudo().search([],limit=500)


        json_dict = {"stock_move_line":[]}
        for stock_move in stock_move_ids:
            sm = { stock_move.id:[{                    
                    "lote": stock_move.lot_id.name or "", #Lote/N° de serie
                    "categ_id": stock_move.product_id.product_tmpl_id.categ_id.x_studio_field_B5Yrj or "", #cod categoria
                    "categoria": stock_move.product_id.product_tmpl_id.categ_id.name or "", #categoria
                    # "rut": stock_move.location_dest_id_barcode or "", #rut (sin digito verificador)
                    "usuario": stock_move.picking_id.partner_id.name or "", #Nombre usuario
                    "codigo_marca": stock_move.product_id.product_tmpl_id.x_studio_field_To4X6.x_cod_marcas_de_at or "", #cod Marca
                    "marca": stock_move.product_id.product_tmpl_id.x_studio_field_To4X6.x_name or "",#Marca
                    # "modelo": stock_move.product_id.product_tmpl_id.x_studio_field_5Bj0L.x_studio_field_5BjOL.x_name or "", #Modelo
                    "referencia_proveedor": stock_move.lot_id.ref or "", #referencia (proveedor)
                    "procesador_at": stock_move.product_id.product_tmpl_id.x_studio_field_E6Mvt.x_name or "", #Procesador_at
                    "velocidad_at": stock_move.product_id.product_tmpl_id.x_studio_field_q1N0G.x_name or "", #Velocidad_at
                    # "memoria_at": stock_move.product_id.product_tmpl_id.x_studio_field_INFQG.x_name or "", #Memoria_at
                    "hdd_at": stock_move.product_id.product_tmpl_id.x_studio_field_WRME0.x_name or "", #Hdd_at
                    "costo_compra_at": stock_move.lot_id.x_studio_costo_compra or "", #Costo compra AT
                    # "proveedor": stock_move.lot_id.purchase_order_ids[0].partner_id.name or "",#proveedor
                    "N_factura": stock_move.lot_id.x_studio_n_factura or "",#N_factura
                    "fecha_compra_at": str(stock_move.lot_id.x_studio_field_6Pp3S),#fecha compra AT
                    "fecha_asignacion": str(stock_move.date) #Fecha asignacion
                    }
                    ]
                }
            json_dict["stock_move_line"].append(sm)
        return json.dumps(json_dict)

    def sql_ids_stock_move_line(self):
        query = """SELECT sml1.id FROM stock_move_line sml1
                    JOIN 
                    (
                    select lot_id, MAX(date) AS MAXDATE from stock_move_line 
                        where lot_id is not null
                        group by lot_id
                    ) sml2
                    ON sml1.lot_id = sml2.lot_id
                    AND sml1.date = sml2.MAXDATE"""
        request.cr.execute(query)
        res = [l for l in request.cr.fetchall()]
        return res or [0]

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