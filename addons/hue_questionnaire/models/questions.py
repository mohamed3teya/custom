from odoo import models, fields


class questionsModel(models.Model):
    _name = 'questions'
    _description = 'questions'
    _inherit = ['mail.thread']


    name = fields.Text( string='question', required=True)
    category = fields.Many2one('question.types', 'category', required=True)
    enable = fields.Boolean()