from odoo import models, fields


class Levels(models.Model):
    _name = 'op.levels'
    _description = 'colleges levels'

    name = fields.Char()
    d_id = fields.Char(string="External ID")