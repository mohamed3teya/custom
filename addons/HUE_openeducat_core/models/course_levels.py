from odoo import fields, models

class CourseLevels(models.Model):
    _name = 'op.course.levels'
    _description = 'op.course.levels'
    _rec_name = 'level_id'
    
    course_id = fields.Many2one('op.course', string='Course', required=True)
    farouk_id = fields.Integer(string='Farouk Mapping')
    hours_from = fields.Integer(string='Hours From', required=True)
    hours_to = fields.Integer(string='Hours To', required=True)
    level_id = fields.Many2one('op.levels', string='Level', required=True)