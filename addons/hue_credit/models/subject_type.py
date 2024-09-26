from odoo import fields, models

class SubjectTypes(models.Model):
    _name= 'op.subjecttypes'
    _description = 'op.subjecttypes'
    
    name = fields.Char()