from odoo import models, fields

class GlobalTerm(models.Model):
    _name = 'hue.global.terms'
    _description = 'GlobalTerm'

    name = fields.Char(required=True)