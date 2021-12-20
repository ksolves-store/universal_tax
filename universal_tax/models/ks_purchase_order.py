import json

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class GlobalTaxPurchases(models.Model):
    _inherit = "purchase.order"

    ks_global_tax_rate = fields.Float(string='Universal Tax (%):', readonly=True,
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_global_tax = fields.Monetary(string="Universal Tax", readonly=True, compute='_amount_all',
                                           track_visibility='always', store=True)
    ks_enable_tax = fields.Boolean(compute='ks_verify_tax')

    @api.depends('company_id.ks_enable_tax')
    def ks_verify_tax(self):
        for rec in self:
            rec.ks_enable_tax = rec.company_id.ks_enable_tax

    @api.depends('order_line.price_total', 'ks_global_tax_rate')
    def _amount_all(self):
        for rec in self:
            ks_res = super(GlobalTaxPurchases, rec)._amount_all()
            if 'amount_discount' in rec:
                rec.ks_calculate_discount()

            rec.ks_calculate_tax()
        return ks_res


    def _prepare_invoice(self):
        ks_res = super(GlobalTaxPurchases, self)._prepare_invoice()
        ks_res['ks_global_tax_rate'] = self.ks_global_tax_rate
        return ks_res

    def action_view_invoice(self, invoices=False):
        for rec in self:
            ks_res = super(GlobalTaxPurchases, rec).action_view_invoice()
            hh = ks_res['context']
            jj = str(hh).replace("'", '"')
            dic = json.loads(jj)
            dic['default_ks_global_tax_rate'] = rec.ks_global_tax_rate
            dic['default_ks_amount_global_tax'] = rec.ks_amount_global_tax
            context_str = json.dumps(dic)
            ks_res['context'] = context_str
            # ks_res['context']['default_ks_global_tax_rate'] = rec.ks_global_tax_rate
            # ks_res['context']['default_ks_amount_global_tax'] = rec.ks_amount_global_tax

        return ks_res

    # @api.multi
    def ks_calculate_tax(self):
        for rec in self:
            if rec.ks_global_tax_rate != 0.0:
                rec.ks_amount_global_tax = (rec.amount_total * rec.ks_global_tax_rate) / 100
            else:
                rec.ks_amount_global_tax = 0.0
            rec.amount_total = rec.ks_amount_global_tax + rec.amount_total

    @api.constrains('ks_global_tax_rate')
    def ks_check_tax_value(self):
        if self.ks_global_tax_rate > 100 or self.ks_global_tax_rate < 0:
            raise ValidationError('You cannot enter percentage value greater than 100 or less than 0.')
