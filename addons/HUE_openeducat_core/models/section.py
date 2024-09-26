from odoo import models, fields

class Section(models.Model):
    _name = 'op.section'
    _description = 'Section'

    name = fields.Char(string="Section Number", required=True)