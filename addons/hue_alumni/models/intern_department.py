from odoo import models, fields


class internDepartment(models.Model):
    _name = 'hue.intern.department'
    _description = 'hue.intern.department'
    _inherit = ['mail.thread']
    _rec_name = 'name'    
    
    
    course_id = fields.Many2one('op.course', string='Course')
    name = fields.Char()
    en_name = fields.Char(string="English name")