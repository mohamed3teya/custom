from odoo import fields, models

class BlockReason(models.Model):
    _name= 'hue.block.reason'
    _description = 'reason to block a student registration or services'
    
    name = fields.Char()