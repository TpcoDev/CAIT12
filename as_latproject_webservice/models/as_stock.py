# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare    
from datetime import datetime, timedelta, date

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        """ Through the interface, we allow users to change the charateristics of a move line. If a
        quantity has been reserved for this move line, we impact the reservation directly to free
        the old quants and allocate the new ones.
        """
        #Se llena fecha asignada si corresponde a una fecha asignada en un "Ajuste de inventario"
        sil_obj = self.env['stock.inventory.line'].sudo().search([('inventory_id','=',self.move_id.inventory_id.id),('product_id','=',self.product_id.id),('prod_lot_id','=',self.lot_id.id)],limit=1,order='id desc')
        if sil_obj:
            if sil_obj.x_studio_fecha_asignacin:
                vals['x_studio_field_BUaym'] = (datetime.strptime(fields.Datetime.to_string(sil_obj.x_studio_fecha_asignacin), '%Y-%m-%d %H:%M:%S')+ timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')
        if self.env.context.get('bypass_reservation_update'):
            return super(StockMoveLine, self).write(vals)

        Quant = self.env['stock.quant']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # We forbid to change the reserved quantity in the interace, but it is needed in the
        # case of stock.move's split.
        # TODO Move me in the update
        if 'product_uom_qty' in vals:
            for ml in self.filtered(lambda m: m.state in ('partially_available', 'assigned') and m.product_id.type == 'product'):
                if not ml.location_id.should_bypass_reservation():
                    qty_to_decrease = ml.product_qty - ml.product_uom_id._compute_quantity(vals['product_uom_qty'], ml.product_id.uom_id, rounding_method='HALF-UP')
                    try:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -qty_to_decrease, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        if ml.lot_id:
                            Quant._update_reserved_quantity(ml.product_id, ml.location_id, -qty_to_decrease, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                        else:
                            raise

        triggers = [
            ('location_id', 'stock.location'),
            ('location_dest_id', 'stock.location'),
            ('lot_id', 'stock.production.lot'),
            ('package_id', 'stock.quant.package'),
            ('result_package_id', 'stock.quant.package'),
            ('owner_id', 'res.partner')
        ]
        updates = {}
        for key, model in triggers:
            if key in vals:
                updates[key] = self.env[model].browse(vals[key])

        if updates:
            for ml in self.filtered(lambda ml: ml.state in ['partially_available', 'assigned'] and ml.product_id.type == 'product'):
                if not ml.location_id.should_bypass_reservation():
                    try:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        if ml.lot_id:
                            Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                        else:
                            raise

                if not updates.get('location_id', ml.location_id).should_bypass_reservation():
                    new_product_qty = 0
                    try:
                        q = Quant._update_reserved_quantity(ml.product_id, updates.get('location_id', ml.location_id), ml.product_qty, lot_id=updates.get('lot_id', ml.lot_id),
                                                             package_id=updates.get('package_id', ml.package_id), owner_id=updates.get('owner_id', ml.owner_id), strict=True)
                        new_product_qty = sum([x[1] for x in q])
                    except UserError:
                        if updates.get('lot_id'):
                            # If we were not able to reserve on tracked quants, we can use untracked ones.
                            try:
                                q = Quant._update_reserved_quantity(ml.product_id, updates.get('location_id', ml.location_id), ml.product_qty, lot_id=False,
                                                                     package_id=updates.get('package_id', ml.package_id), owner_id=updates.get('owner_id', ml.owner_id), strict=True)
                                new_product_qty = sum([x[1] for x in q])
                            except UserError:
                                pass
                    if new_product_qty != ml.product_qty:
                        new_product_uom_qty = ml.product_id.uom_id._compute_quantity(new_product_qty, ml.product_uom_id, rounding_method='HALF-UP')
                        ml.with_context(bypass_reservation_update=True).product_uom_qty = new_product_uom_qty

        # When editing a done move line, the reserved availability of a potential chained move is impacted. Take care of running again `_action_assign` on the concerned moves.
        next_moves = self.env['stock.move']
        if updates or 'qty_done' in vals:
            for ml in self.filtered(lambda ml: ml.move_id.state == 'done' and ml.product_id.type == 'product'):
                # undo the original move line
                qty_done_orig = ml.move_id.product_uom._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                in_date = Quant._update_available_quantity(ml.product_id, ml.location_dest_id, -qty_done_orig, lot_id=ml.lot_id,
                                                      package_id=ml.result_package_id, owner_id=ml.owner_id)[1]
                Quant._update_available_quantity(ml.product_id, ml.location_id, qty_done_orig, lot_id=ml.lot_id,
                                                      package_id=ml.package_id, owner_id=ml.owner_id, in_date=in_date)

                # move what's been actually done
                product_id = ml.product_id
                location_id = updates.get('location_id', ml.location_id)
                location_dest_id = updates.get('location_dest_id', ml.location_dest_id)
                qty_done = vals.get('qty_done', ml.qty_done)
                lot_id = updates.get('lot_id', ml.lot_id)
                package_id = updates.get('package_id', ml.package_id)
                result_package_id = updates.get('result_package_id', ml.result_package_id)
                owner_id = updates.get('owner_id', ml.owner_id)
                quantity = ml.move_id.product_uom._compute_quantity(qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                if not location_id.should_bypass_reservation():
                    ml._free_reservation(product_id, location_id, quantity, lot_id=lot_id, package_id=package_id, owner_id=owner_id)
                if not float_is_zero(quantity, precision_digits=precision):
                    available_qty, in_date = Quant._update_available_quantity(product_id, location_id, -quantity, lot_id=lot_id, package_id=package_id, owner_id=owner_id)
                    if available_qty < 0 and lot_id:
                        # see if we can compensate the negative quants with some untracked quants
                        untracked_qty = Quant._get_available_quantity(product_id, location_id, lot_id=False, package_id=package_id, owner_id=owner_id, strict=True)
                        if untracked_qty:
                            taken_from_untracked_qty = min(untracked_qty, abs(available_qty))
                            Quant._update_available_quantity(product_id, location_id, -taken_from_untracked_qty, lot_id=False, package_id=package_id, owner_id=owner_id)
                            Quant._update_available_quantity(product_id, location_id, taken_from_untracked_qty, lot_id=lot_id, package_id=package_id, owner_id=owner_id)
                            if not location_id.should_bypass_reservation():
                                ml._free_reservation(ml.product_id, location_id, untracked_qty, lot_id=False, package_id=package_id, owner_id=owner_id)
                    Quant._update_available_quantity(product_id, location_dest_id, quantity, lot_id=lot_id, package_id=result_package_id, owner_id=owner_id, in_date=in_date)

                # Unreserve and reserve following move in order to have the real reserved quantity on move_line.
                next_moves |= ml.move_id.move_dest_ids.filtered(lambda move: move.state not in ('done', 'cancel'))

                # Log a note
                if ml.picking_id:
                    ml._log_message(ml.picking_id, ml, 'stock.track_move_template', vals)

        res = super(StockMoveLine, self).write(vals)

        # Update scrap object linked to move_lines to the new quantity.
        if 'qty_done' in vals:
            for move in self.mapped('move_id'):
                if move.scrapped:
                    move.scrap_ids.write({'scrap_qty': move.quantity_done})

        # As stock_account values according to a move's `product_uom_qty`, we consider that any
        # done stock move should have its `quantity_done` equals to its `product_uom_qty`, and
        # this is what move's `action_done` will do. So, we replicate the behavior here.
        if updates or 'qty_done' in vals:
            moves = self.filtered(lambda ml: ml.move_id.state == 'done').mapped('move_id')
            for move in moves:
                move.product_uom_qty = move.quantity_done
        next_moves._do_unreserve()
        next_moves._action_assign()
        return res