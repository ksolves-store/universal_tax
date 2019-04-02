from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class KsGlobalTaxInvoice(models.Model):
    _inherit = "account.invoice"

    ks_global_tax_rate = fields.Float(string='Universal Tax (%):', readonly=True,
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_global_tax = fields.Monetary(string="Universal Tax", readonly=True, compute='_compute_amount',
                                           track_visibility='always', store=True)
    ks_enable_tax = fields.Boolean(compute='ks_verify_tax')
    ks_sales_tax_account = fields.Text(compute='ks_verify_tax')
    ks_purchase_tax_account = fields.Text(compute='ks_verify_tax')

    @api.multi
    @api.depends('name')
    def ks_verify_tax(self):
        for rec in self:
            rec.ks_enable_tax = rec.env['ir.config_parameter'].sudo().get_param('ks_enable_tax')
            rec.ks_sales_tax_account = rec.env['ir.config_parameter'].sudo().get_param('ks_sales_tax_account')
            rec.ks_purchase_tax_account = rec.env['ir.config_parameter'].sudo().get_param('ks_purchase_tax_account')

    @api.multi
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'ks_global_tax_rate')
    def _compute_amount(self):
        for rec in self:
            ks_res = super(KsGlobalTaxInvoice, rec)._compute_amount()
            if 'ks_amount_discount' in rec:
                rec.ks_calculate_discount()
            rec.ks_calculate_tax()
            sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_company_signed = rec.amount_total * sign
            rec.amount_total_signed = rec.amount_total * sign
        return ks_res

    @api.multi
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
            raise ValidationError('You cannot enter percentage value greater than 100.')

    @api.onchange('purchase_id')
    def get_purchase_order_tax(self):
        self.ks_global_tax_rate = self.purchase_id.ks_global_tax_rate
        self.ks_amount_global_tax = self.purchase_id.ks_amount_global_tax

    @api.model
    def invoice_line_move_line_get(self):
        ks_res = super(KsGlobalTaxInvoice, self).invoice_line_move_line_get()
        if self.ks_amount_global_tax > 0:
            ks_name = "Universal Tax"
            ks_name = ks_name + " (" + str(self.ks_global_tax_rate) + "%)"
            ks_name = ks_name + " for " + (self.origin if self.origin else ("Invoice No " + str(self.id)))
            if self.ks_sales_tax_account and (self.type == "out_invoice" or self.type == "out_refund"):
                dict = {
                    'invl_id': self.number,
                    'type': 'src',
                    'name': ks_name,
                    'price_unit': self.ks_amount_global_tax,
                    'quantity': 1,
                    'price': self.ks_amount_global_tax,
                    'account_id': int(self.ks_sales_tax_account),
                    'invoice_id': self.id,
                }
                ks_res.append(dict)

            elif self.ks_purchase_tax_account and (self.type == "in_invoice" or self.type == "in_refund"):
                dict = {
                    'invl_id': self.number,
                    'type': 'src',
                    'name': ks_name,
                    'price_unit': self.ks_amount_global_tax,
                    'quantity': 1,
                    'price': self.ks_amount_global_tax,
                    'account_id': int(self.ks_purchase_tax_account),
                    'invoice_id': self.id,
                }
                ks_res.append(dict)
        return ks_res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        ks_res = super(KsGlobalTaxInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                 description=None, journal_id=None)
        ks_res['ks_global_tax_rate'] = self.ks_global_tax_rate
        ks_res['ks_amount_global_tax'] = self.ks_amount_global_tax
        return ks_res
