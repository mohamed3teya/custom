from odoo import models, fields


class questionTypesModel(models.Model):
    _name = 'question.types'
    _description = 'question.types'
    _inherit = ['mail.thread']
    _rec_name = 'category_name'


    category_name = fields.Char( string='Category name', required=True)
    enable = fields.Boolean()
    types = fields.Selection([('subject', 'subject'), ('doctor', 'doctor'),('assistant', 'assistant'),('service', 'service')])