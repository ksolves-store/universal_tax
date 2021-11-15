from odoo import fields, models


class KsGlobalResCompany(models.Model):

    _inherit = "res.company"

    ks_enable_tax = fields.Boolean(string='Enable Global Tax')