# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class KsGlobalTaxSales(models.Model):
    _inherit = "sale.order"

    ks_global_tax_rate = fields.Float(string="Universal Tax (%):", readonly=True,
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_global_tax = fields.Monetary(string='Universal Tax', readonly=True, compute='_amount_all',
                                           track_visibility='always', store=True)
    ks_enable_tax = fields.Boolean(compute='ks_verify_tax')

    @api.depends('company_id.ks_enable_tax')
    def ks_verify_tax(self):
        for rec in self:
            rec.ks_enable_tax = rec.company_id.ks_enable_tax

    @api.depends('order_line.price_total', 'ks_global_tax_rate')
    def _amount_all(self):
        for rec in self:
            ks_res = super(KsGlobalTaxSales, rec)._amount_all()
            if 'ks_amount_discount' in rec:
                rec.ks_calculate_discount()

            rec.ks_calculate_tax()
        return ks_res

    def _prepare_invoice(self):
        for rec in self:
            ks_res = super(KsGlobalTaxSales, rec)._prepare_invoice()
            ks_res['ks_global_tax_rate'] = rec.ks_global_tax_rate
            ks_res['ks_amount_global_tax'] = rec.ks_amount_global_tax
        return ks_res

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


class KsSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(KsSaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if invoice:
            invoice['ks_global_tax_rate'] = order.ks_global_tax_rate
            invoice['ks_amount_global_tax'] = order.ks_amount_global_tax
        return invoice
