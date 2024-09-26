from odoo import fields, models

class CustomFeesTerms(models.Model):
    _inherit = 'op.fees.terms'
    
    years_id = fields.Many2one('hue.years', string="Years")
    one_time = fields.Boolean(string="One Time", default=False)
    foreign_nationality = fields.Boolean(string="Foreign Nationality", default=False)
    currency = fields.Many2one('res.currency')
    term_id = fields.Many2one('hue.global.terms', string="Global Term")
    extra_inv = fields.Boolean(string="Extra Inv")
    special_case = fields.Boolean(string="Special Case")