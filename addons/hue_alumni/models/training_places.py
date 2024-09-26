from odoo import models, fields


class trainingPlaces(models.Model):
    _name = 'hue.training.places'
    _description ='hue.training.places'
    _inherit = ['mail.thread']
    _rec_name = 'name'    
    
    
    name = fields.Char()
    en_name = fields.Char(string="English name")
    training_type = fields.Selection([('internal', 'internal'), ('external', 'external')])