from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_enable_tax = fields.Boolean(string="Activate Universal Tax")
    ks_sales_tax_account = fields.Many2one('account.account', string="Sales Tax Account")
    ks_purchase_tax_account = fields.Many2one('account.account', string="Purchase Tax Account")


class KsResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_enable_tax = fields.Boolean(string="Activate Universal Tax", related='company_id.ks_enable_tax', readonly=False)
    ks_sales_tax_account = fields.Many2one('account.account', string="Sales Tax Account", related='company_id.ks_sales_tax_account', readonly=False)
    ks_purchase_tax_account = fields.Many2one('account.account', string="Purchase Tax Account", related='company_id.ks_purchase_tax_account', readonly=False)
