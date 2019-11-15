from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class KsGlobalTaxInvoice(models.Model):
    # _inherit = "account.invoice"
    _inherit = "account.move"

    ks_global_tax_rate = fields.Float(string='Universal Tax (%):', readonly=True,
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_global_tax = fields.Monetary(string="Universal Tax", readonly=True, compute='_compute_amount',
                                           track_visibility='always', store=True)
    ks_enable_tax = fields.Boolean(compute='ks_verify_tax')
    ks_sales_tax_account = fields.Integer(compute='ks_verify_tax')
    ks_purchase_tax_account = fields.Integer(compute='ks_verify_tax')

    # @api.multi
    @api.depends('name')
    def ks_verify_tax(self):
        for rec in self:
            rec.ks_enable_tax = rec.env['ir.config_parameter'].sudo().get_param('ks_enable_tax')
            rec.ks_sales_tax_account = rec.env['ir.config_parameter'].sudo().get_param('ks_sales_tax_account')
            rec.ks_purchase_tax_account = rec.env['ir.config_parameter'].sudo().get_param('ks_purchase_tax_account')

    # @api.multi
    # @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
    #              'currency_id', 'company_id', 'date_invoice', 'type', 'ks_global_tax_rate')
    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'ks_global_tax_rate')
    def _compute_amount(self):
        for rec in self:
            ks_res = super(KsGlobalTaxInvoice, rec)._compute_amount()
            if 'ks_amount_discount' in rec:
                rec.ks_calculate_discount()

            rec.ks_calculate_tax()
            rec.ks_update_universal_tax()
            sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_company_signed = rec.amount_total * sign
            rec.amount_total_signed = rec.amount_total * sign
        return ks_res

    # @api.multi
    def ks_calculate_tax(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.ks_global_tax_rate != 0.0 and rec.type in type_list:
                rec.ks_amount_global_tax = (rec.amount_total * rec.ks_global_tax_rate) / 100
            else:
                rec.ks_amount_global_tax = 0.0

            rec.amount_total = rec.ks_amount_global_tax + rec.amount_total

    def ks_update_universal_tax(self):
        for rec in self:
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Universal Tax') == 0)
            terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            other_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
            if already_exists:
                amount = rec.ks_amount_global_tax
                if rec.ks_sales_tax_account \
                        and (rec.type == "out_invoice"
                             or rec.type == "out_refund")\
                        and rec.ks_global_tax_rate > 0:
                    if rec.type == "out_invoice":
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                if rec.ks_purchase_tax_account \
                        and (rec.type == "in_invoice"
                             or rec.type == "in_refund")\
                        and rec.ks_global_tax_rate > 0:
                    if rec.type == "in_invoice":
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                terms_lines.update({
                    'amount_currency': -total_amount_currency,
                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                    'credit': total_balance > 0.0 and total_balance or 0.0,
                })
            if not already_exists and rec.ks_global_tax_rate > 0:
                in_draft_mode = self != self._origin
                if not in_draft_mode:
                    rec._recompute_universal_tax_lines()
                print()

    @api.constrains('ks_global_tax_rate')
    def ks_check_tax_value(self):
        if self.ks_global_tax_rate > 100 or self.ks_global_tax_rate < 0:
            raise ValidationError('You cannot enter percentage value greater than 100.')

    # @api.onchange('purchase_id')
    # def get_purchase_order_tax(self):
    #     self.ks_global_tax_rate = self.purchase_id.ks_global_tax_rate
    #     self.ks_amount_global_tax = self.purchase_id.ks_amount_global_tax

    # @api.model
    # def invoice_line_move_line_get(self):
    #     ks_res = super(KsGlobalTaxInvoice, self).invoice_line_move_line_get()
    #     if self.ks_amount_global_tax > 0:
    #         ks_name = "Universal Tax"
    #         ks_name = ks_name + " (" + str(self.ks_global_tax_rate) + "%)"
    #         ks_name = ks_name + " for " + (self.origin if self.origin else ("Invoice No " + str(self.id)))
    #         if self.ks_sales_tax_account and (self.type == "out_invoice" or self.type == "out_refund"):
    #             dict = {
    #                 'invl_id': self.number,
    #                 'type': 'src',
    #                 'name': ks_name,
    #                 'price_unit': self.ks_amount_global_tax,
    #                 'quantity': 1,
    #                 'price': self.ks_amount_global_tax,
    #                 'account_id': int(self.ks_sales_tax_account),
    #                 'invoice_id': self.id,
    #             }
    #             ks_res.append(dict)
    #
    #         elif self.ks_purchase_tax_account and (self.type == "in_invoice" or self.type == "in_refund"):
    #             dict = {
    #                 'invl_id': self.number,
    #                 'type': 'src',
    #                 'name': ks_name,
    #                 'price_unit': self.ks_amount_global_tax,
    #                 'quantity': 1,
    #                 'price': self.ks_amount_global_tax,
    #                 'account_id': int(self.ks_purchase_tax_account),
    #                 'invoice_id': self.id,
    #             }
    #             ks_res.append(dict)
    #     return ks_res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        ks_res = super(KsGlobalTaxInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                 description=None, journal_id=None)
        ks_res['ks_global_tax_rate'] = self.ks_global_tax_rate
        ks_res['ks_amount_global_tax'] = self.ks_amount_global_tax
        return ks_res

    @api.onchange('ks_global_tax_rate', 'line_ids')
    def _recompute_universal_tax_lines(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.ks_global_tax_rate > 0 and rec.type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    ks_name = "Universal Tax"
                    ks_name = ks_name + \
                              " @" + str(self.ks_global_tax_rate) + "%"
                    # ks_name = ks_name + " for " + \
                    #           ("Invoice No: " + str(self.ids)
                    #            if self._origin.id
                    #            else (self.display_name))
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    already_exists = self.line_ids.filtered(
                                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                    if already_exists:
                        amount = self.ks_amount_global_tax
                        if self.ks_sales_tax_account \
                                and (self.type == "out_invoice"
                                     or self.type == "out_refund"):
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                            })
                        if self.ks_purchase_tax_account\
                                and (self.type == "in_invoice"
                                     or self.type == "in_refund"):
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                            })
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or\
                                        self.env['account.move.line'].create

                        if self.ks_sales_tax_account \
                                and (self.type == "out_invoice"
                                     or self.type == "out_refund"):
                            amount = self.ks_amount_global_tax
                            dict = {
                                    'move_name': self.name,
                                    'name': ks_name,
                                    'price_unit': self.ks_amount_global_tax,
                                    'quantity': 1,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                    'account_id': int(self.ks_purchase_tax_account),
                                    'move_id': self._origin,
                                    'date': self.date,
                                    'exclude_from_invoice_tab': True,
                                    'partner_id': terms_lines.partner_id.id,
                                    'company_id': terms_lines.company_id.id,
                                    'company_currency_id': terms_lines.company_currency_id.id,
                                    }
                            if self.type == "out_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    'price_unit': 0.0,
                                    'debit': 0.0,
                                    'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]

                        if self.ks_purchase_tax_account\
                                and (self.type == "in_invoice"
                                     or self.type == "in_refund"):
                            amount = self.ks_amount_global_tax
                            dict = {
                                    'move_name': self.name,
                                    'name': ks_name,
                                    'price_unit': self.ks_amount_global_tax,
                                    'quantity': 1,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                    'account_id': int(self.ks_sales_tax_account),
                                    'move_id': self.id,
                                    'date': self.date,
                                    'exclude_from_invoice_tab': True,
                                    'partner_id': terms_lines.partner_id.id,
                                    'company_id': terms_lines.company_id.id,
                                    'company_currency_id': terms_lines.company_currency_id.id,
                                    }

                            if self.type == "in_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            self.line_ids += create_method(dict)
                            # updation of invoice line id
                            duplicate_id = self.invoice_line_ids.filtered(
                                lambda line: line.name and line.name.find('Universal Tax') == 0)
                            self.invoice_line_ids = self.invoice_line_ids - duplicate_id

                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                                    'amount_currency': -total_amount_currency,
                                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                                    'credit': total_balance > 0.0 and total_balance or 0.0,
                                })
                    else:
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        already_exists = self.line_ids.filtered(
                            lambda line: line.name and line.name.find('Universal Tax') == 0)
                        total_balance = sum(other_lines.mapped('balance')) - amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                        }
                        dict2 = {
                                'debit': total_balance < 0.0 and -total_balance or 0.0,
                                'credit': total_balance > 0.0 and total_balance or 0.0,
                                }
                        self.line_ids = [(1, already_exists.id, dict1), (1, terms_lines.id, dict2)]
                        print()

            elif self.ks_global_tax_rate <= 0:
                already_exists = self.line_ids.filtered(
                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                if already_exists:
                    self.line_ids -= already_exists
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    other_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })
