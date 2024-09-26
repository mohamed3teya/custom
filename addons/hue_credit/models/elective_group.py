from odoo import fields, models

class ElectiveGroup(models.Model):
    _name = 'op.elective.groups'
    _description = 'op.elective.groups'
    
    count = fields.Integer()
    course_id = fields.Many2one('op.course', string='Course')
    name= fields.Char()
    
    