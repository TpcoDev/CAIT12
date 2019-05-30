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
    @http.route('/webservice/stock1', auth='public', methods=['POST'], type="json", csrf=False)
    def index(self, **kw):
        stock_picking_model = request.env['stock.picking']
        stock_picking_ids = stock_picking_model.sudo().search([], limit=10)


        json_dict = {"stock_picking":[]}
        for stock_picking in stock_picking_ids:
            sp = { stock_picking.id:[{
                    "id":stock_picking.id,
                    "origin":stock_picking.origin,
                    "state":stock_picking.state,
                    "partner":stock_picking.partner_id.name
                    }
                    ]
                }
            json_dict["stock_picking"].append(sp)
        return json.dumps(json_dict)