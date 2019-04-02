from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KsResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_enable_tax = fields.Boolean(string="Activate Universal Tax")
    ks_sales_tax_account = fields.Many2one('account.account', string="Sales Tax Account")
    ks_purchase_tax_account = fields.Many2one('account.account', string="Purchase Tax Account")

    def get_values(self):
        ks_res = super(KsResConfigSettings, self).get_values()
        ks_res.update(
            ks_enable_tax=self.env['ir.config_parameter'].sudo().get_param('ks_enable_tax'),
            ks_sales_tax_account=int(self.env['ir.config_parameter'].sudo().get_param('ks_sales_tax_account')),
            ks_purchase_tax_account=int(self.env['ir.config_parameter'].sudo().get_param('ks_purchase_tax_account')),
        )
        return ks_res

    def set_values(self):
        super(KsResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('ks_enable_tax', self.ks_enable_tax)
        if self.ks_enable_tax:
            self.env['ir.config_parameter'].set_param('ks_sales_tax_account', self.ks_sales_tax_account.id)
            self.env['ir.config_parameter'].set_param('ks_purchase_tax_account', self.ks_purchase_tax_account.id)

