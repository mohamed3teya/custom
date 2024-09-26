from odoo import fields, models

class CourseLoadHours(models.Model):
    _name = 'op.course.loadhours'
    _description = 'op.course.loadhours'
    
    course_id = fields.Many2one('op.course', string='Course',required=True)
    gpa_from = fields.Float(string='GPA From',required=True)
    gpa_to = fields.Float(string='GPA To',required=True)
    hours_from = fields.Integer(string='Hours From',required=True)
    hours_to = fields.Integer(string='Hours To',required=True)
    level_id = fields.Many2one('op.levels', string='Level')
    semester_id = fields.Many2one('op.semesters', string='Semester')